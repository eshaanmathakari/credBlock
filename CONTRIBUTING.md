# Contributing to CredBlock

Thank you for your interest in contributing to CredBlock! We welcome contributions from the community and appreciate your help in making this project better.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- Docker Desktop
- Git

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/eshaanmathakari/credBlock.git
   cd credblock
   ```
3. Set up the development environment:
   ```bash
   ./start-local.sh
   ```

## 📋 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker
- Provide clear descriptions and steps to reproduce
- Include relevant logs and system information

### Suggesting Features
- Open a GitHub issue with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity

### Code Contributions
1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🧪 Testing

### Backend Testing
```bash
cd backend
source venv/bin/activate
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Test the full stack
./start-local.sh
# Run integration tests
npm run test:integration
```

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions small and focused

### TypeScript/React
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling

### Git Commit Messages
- Use conventional commits format
- Be descriptive and concise
- Reference issues when applicable

## 🔧 Development Guidelines

### Backend Development
- Use FastAPI best practices
- Implement proper error handling
- Add logging for debugging
- Cache expensive operations

### Frontend Development
- Use shadcn/ui components
- Follow the design system
- Implement responsive design
- Add loading states and error handling

### Blockchain Integration
- Test with testnet first
- Handle network errors gracefully
- Implement proper rate limiting
- Cache blockchain data appropriately

## 🐛 Bug Fixes

When fixing bugs:
1. Reproduce the issue
2. Write a test that fails
3. Fix the code
4. Ensure the test passes
5. Update documentation if needed

## ✨ New Features

When adding features:
1. Discuss in an issue first
2. Design the API/interface
3. Implement with tests
4. Update documentation
5. Add examples

## 📚 Documentation

- Update README.md for major changes
- Add inline code documentation
- Update API documentation
- Include usage examples

## 🔒 Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all inputs
- Follow security best practices

## 🎯 Areas for Contribution

- **Frontend**: UI/UX improvements, new components
- **Backend**: Performance optimizations, new APIs
- **Blockchain**: Additional chain support, new integrations
- **ML**: Model improvements, new features
- **DevOps**: Deployment improvements, monitoring
- **Documentation**: Guides, tutorials, examples

## 📞 Getting Help

- Join our Discord community
- Ask questions in GitHub Discussions
- Check existing issues and PRs
- Review the codebase

## 🏆 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Invited to the core team for significant contributions

Thank you for contributing to CredBlock! 🚀
