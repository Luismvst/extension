"""
Business rules engine for order processing.

This module implements a flexible rules engine that can determine
which carrier to use based on order characteristics and business rules.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from ..adapters.interfaces.marketplace import Order
from ..core.logging import get_logger

logger = get_logger(__name__)


class CarrierType(Enum):
    """Available carrier types."""
    TIPSA = "tipsa"
    DHL = "dhl"
    UPS = "ups"
    FEDEX = "fedex"


@dataclass
class Rule:
    """A business rule for carrier selection."""
    name: str
    condition: Callable[[Order], bool]
    carrier: CarrierType
    priority: int = 0
    description: str = ""


class RulesEngine:
    """
    Business rules engine for determining carrier selection.
    
    This engine evaluates orders against a set of rules to determine
    which carrier should be used for shipping.
    """
    
    def __init__(self, rules_config_path: Optional[str] = None):
        """Initialize the rules engine."""
        self.rules: List[Rule] = []
        self.rules_config_path = rules_config_path
        self._load_default_rules()
        
        if rules_config_path:
            self._load_rules_from_config()
    
    def _load_default_rules(self) -> None:
        """Load default business rules."""
        # Rule 1: Heavy packages go to TIPSA
        self.add_rule(Rule(
            name="heavy_packages",
            condition=lambda order: order.weight > 20.0,
            carrier=CarrierType.TIPSA,
            priority=100,
            description="Packages over 20kg go to TIPSA"
        ))
        
        # Rule 2: COD orders go to TIPSA
        self.add_rule(Rule(
            name="cod_orders",
            condition=lambda order: order.cod_amount is not None and order.cod_amount > 0,
            carrier=CarrierType.TIPSA,
            priority=90,
            description="COD orders go to TIPSA"
        ))
        
        # Rule 3: Express service goes to DHL
        self.add_rule(Rule(
            name="express_service",
            condition=lambda order: order.service_type == "express",
            carrier=CarrierType.DHL,
            priority=80,
            description="Express service goes to DHL"
        ))
        
        # Rule 4: International orders go to DHL
        self.add_rule(Rule(
            name="international_orders",
            condition=lambda order: order.shipping_address.country != "ES",
            carrier=CarrierType.DHL,
            priority=70,
            description="International orders go to DHL"
        ))
        
        # Rule 5: Default to TIPSA
        self.add_rule(Rule(
            name="default_tipsa",
            condition=lambda order: True,
            carrier=CarrierType.TIPSA,
            priority=0,
            description="Default carrier is TIPSA"
        ))
    
    def _load_rules_from_config(self) -> None:
        """Load rules from configuration file."""
        if not self.rules_config_path:
            return
            
        config_path = Path(self.rules_config_path)
        if not config_path.exists():
            logger.warning(f"Rules config file not found: {self.rules_config_path}")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Clear existing rules
            self.rules = []
            
            # Load rules from config
            for rule_config in config.get('rules', []):
                rule = self._create_rule_from_config(rule_config)
                if rule:
                    self.add_rule(rule)
                    
            logger.info(f"Loaded {len(self.rules)} rules from config")
            
        except Exception as e:
            logger.error(f"Error loading rules config: {e}")
            # Fallback to default rules
            self._load_default_rules()
    
    def _create_rule_from_config(self, rule_config: Dict[str, Any]) -> Optional[Rule]:
        """Create a rule from configuration."""
        try:
            name = rule_config['name']
            carrier = CarrierType(rule_config['carrier'])
            priority = rule_config.get('priority', 0)
            description = rule_config.get('description', '')
            
            # Create condition function from config
            condition_type = rule_config.get('condition_type')
            condition_value = rule_config.get('condition_value')
            
            if condition_type == 'weight_gt':
                condition = lambda order, value=condition_value: order.weight > value
            elif condition_type == 'cod_gt':
                condition = lambda order, value=condition_value: (
                    order.cod_amount is not None and order.cod_amount > value
                )
            elif condition_type == 'service_type':
                condition = lambda order, value=condition_value: order.service_type == value
            elif condition_type == 'country_ne':
                condition = lambda order, value=condition_value: order.shipping_address.country != value
            elif condition_type == 'always':
                condition = lambda order: True
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return None
            
            return Rule(
                name=name,
                condition=condition,
                carrier=carrier,
                priority=priority,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error creating rule from config: {e}")
            return None
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine."""
        self.rules.append(rule)
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.debug(f"Added rule: {rule.name} (priority: {rule.priority})")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                logger.debug(f"Removed rule: {rule_name}")
                return True
        return False
    
    def get_carrier_for_order(self, order: Order) -> CarrierType:
        """
        Determine which carrier should be used for an order.
        
        Args:
            order: The order to evaluate
            
        Returns:
            The recommended carrier type
        """
        for rule in self.rules:
            try:
                if rule.condition(order):
                    logger.debug(
                        f"Order {order.order_id} matched rule '{rule.name}': {rule.description}"
                    )
                    return rule.carrier
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}")
                continue
        
        # Fallback to TIPSA if no rules match
        logger.warning(f"No rules matched for order {order.order_id}, using default TIPSA")
        return CarrierType.TIPSA
    
    def get_applicable_rules(self, order: Order) -> List[Rule]:
        """
        Get all rules that apply to an order.
        
        Args:
            order: The order to evaluate
            
        Returns:
            List of applicable rules
        """
        applicable = []
        for rule in self.rules:
            try:
                if rule.condition(order):
                    applicable.append(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}")
                continue
        
        return applicable
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get a summary of all rules."""
        return {
            "total_rules": len(self.rules),
            "rules": [
                {
                    "name": rule.name,
                    "carrier": rule.carrier.value,
                    "priority": rule.priority,
                    "description": rule.description
                }
                for rule in self.rules
            ]
        }
