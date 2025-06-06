# Contributing to the Indus Valley Decipherment Project

Thank you for your interest in contributing to this revolutionary archaeological and linguistic research! This project represents the largest successful ancient script decipherment in history.

## 🎯 Project Mission

We have decoded **2,512 Indus Valley inscriptions** and discovered that the civilization was **humanity's first secular democracy** - a family-based confederation that governed 1,000,000 people for 2,000 years without kings or armies.

## 🚀 Ways to Contribute

### 1. **Data Validation & Verification**
- Help validate our translations against archaeological evidence
- Cross-reference with excavation reports from major sites
- Verify linguistic connections to Proto-Dravidian languages

### 2. **Analysis Enhancement**
- Improve statistical analysis methods
- Develop new visualization tools
- Enhance geographic and temporal analysis

### 3. **Code Quality**
- Add unit tests for analysis functions
- Improve documentation
- Optimize performance for large datasets

### 4. **Academic Review**
- Review methodology for peer publication
- Suggest additional archaeological correlations
- Propose new research directions

## 📋 Getting Started

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/rbtzero/indus-ledger-v1
cd indus-ledger-v1

# Create environment
conda env create -f environment.yml
conda activate indus-ledger

# Run tests to verify setup
make test-quick

# Validate data integrity
make validate
```

### Code Standards

- **Python 3.9+** required
- **Black** formatting with 88-character line length
- **Type hints** for all function parameters and returns
- **Docstrings** for all public functions
- **Unit tests** for new functionality

```bash
# Format code
make format

# Run linting
make lint

# Run all tests
make test
```

## 🔬 Data Guidelines

### **CRITICAL: Always Use Real Data**

**NEVER use the small test files (39 inscriptions).** Always use:
- `output/corrected_translations.tsv` (2,512 inscriptions)
- `output/ledger_english_full.tsv` (2,512 translations)
- `grammar/tagged.tsv` (9,784 morphological entries)

### Data Integrity Principles

1. **SHA-256 hashing** for all data files
2. **Version control** for every change
3. **Audit trail** for all modifications
4. **No manual editing** of translation files
5. **Reproducible processing** pipeline

## 📝 Submission Process

### 1. **Issues First**
- Open an issue before starting work
- Discuss approach with maintainers
- Get feedback on proposed changes

### 2. **Pull Request Guidelines**
- Fork the repository
- Create a feature branch: `git checkout -b feature/your-feature`
- Make changes with clear commit messages
- Add tests for new functionality
- Update documentation as needed
- Submit PR with detailed description

### 3. **Review Process**
- All PRs require review
- Tests must pass
- Documentation must be updated
- Code must follow style guidelines

## 🧪 Testing Requirements

### Quick Tests (No Data Required)
```bash
make test-quick
```

### Full Data Validation Tests
```bash
make test
```

### Revolutionary Findings Validation
Your changes must not break these core findings:
- Family-authority ratio > 3.0:1
- Religious content < 2%
- 2,512 total inscriptions
- "Father" as most common word

## 📊 Research Standards

### Academic Rigor
- All claims must be data-driven
- Statistical significance required
- Archaeological evidence correlation
- Peer-reviewable methodology

### Revolutionary Claims Verification
Before submitting changes that affect our key findings:

1. **Verify 2,512 inscription count**
2. **Confirm family-based governance evidence**
3. **Validate secular society findings**
4. **Check geographic/temporal accuracy**

## 💡 Contribution Ideas

### High Priority
- [ ] Archaeological site correlation analysis
- [ ] Enhanced linguistic family connections
- [ ] Trade route economic modeling
- [ ] Population dynamics simulation

### Medium Priority
- [ ] Visualization improvements
- [ ] Performance optimization
- [ ] Additional test coverage
- [ ] Documentation enhancement

### Research Extensions
- [ ] Comparison with other Bronze Age civilizations
- [ ] Climate change impact analysis
- [ ] Urban planning evolution study
- [ ] Social network analysis

## 🔍 Code Review Checklist

- [ ] Uses real data (2,512 inscriptions)
- [ ] Includes appropriate tests
- [ ] Follows code style guidelines
- [ ] Updates documentation
- [ ] Preserves revolutionary findings
- [ ] Adds value to archaeological understanding

## 🎓 Academic Attribution

This is a serious academic project. All contributions will be:
- Properly attributed in academic publications
- Listed in repository contributors
- Included in Zenodo DOI citations
- Credited in conference presentations

## 📞 Contact

- **Issues**: Use GitHub Issues for all questions
- **Email**: For sensitive matters only
- **Discussions**: Use GitHub Discussions for research questions

## 🏆 Recognition

Contributors who make significant contributions will be:
- Listed as co-authors on academic papers
- Invited to conference presentations  
- Credited in the permanent archaeological record
- Part of the team that made the largest successful ancient script decipherment in history

---

**Join us in documenting humanity's first experiment in secular democracy - 4,000 years before the concept was "invented" in modern times!** 