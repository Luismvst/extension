# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and documentation
- Chrome Extension MV3 architecture design
- FastAPI backend structure planning
- Docker and CI/CD pipeline design

## [0.1.0] - 2024-01-15

### Added
- Chrome Extension MV3 with React + TypeScript + Tailwind
- CSV interception for Mirakl marketplaces (Carrefour, Leroy, Adeo)
- OrderStandard data model with Zod validation
- TIPSA CSV mapper for carrier integration
- Popup UI for order management and CSV generation
- Background service worker for queue management
- FastAPI backend with Pydantic models
- Docker containerization for backend and extension build
- GitHub Actions CI/CD pipeline
- Playwright E2E tests with fake portal
- Comprehensive documentation (README, Architecture, MVP Plan)
- MIT License and project setup

### Technical Details
- **Extension**: Vite + React 18 + TypeScript 5 + Tailwind CSS 3
- **Backend**: FastAPI + Pydantic + Uvicorn
- **Testing**: Jest + Playwright + Pytest
- **CI/CD**: GitHub Actions with automated testing and building
- **Containerization**: Docker + Docker Compose
- **Code Quality**: ESLint + Prettier + TypeScript strict mode

### Security
- PII minimization and light obfuscation
- Local storage with ephemeral data
- Structured logging without sensitive information
- Input validation with Zod schemas

### Performance
- CSV parsing with PapaParse for optimal performance
- Chrome storage API for efficient data persistence
- Background processing to avoid UI blocking
- Optimized bundle size with Vite tree-shaking

## [0.0.1] - 2024-01-15

### Added
- Initial project setup
- Project documentation and architecture planning
- Repository structure and configuration files
