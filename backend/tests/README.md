# AeroRhythm POC - Comprehensive Testing Suite

This directory contains a comprehensive testing framework for the AeroRhythm crew rostering system POC. The testing suite covers all aspects of the system from frontend UI components to backend APIs, database operations, and end-to-end workflows.

## 🧪 Test Suites Overview

### 1. Frontend Testing (`test_frontend.py`)
Tests all frontend functionality including:
- **Build Process**: npm install, build compilation
- **Dev Server**: Development server startup and accessibility
- **UI Components**: Component structure and rendering
- **Routing**: Frontend routing configuration
- **API Integration**: Frontend-backend API client setup
- **Responsive Design**: Mobile and desktop compatibility

**Usage:**
```bash
cd backend/tests
python test_frontend.py
```

### 2. Backend Testing (`test_backend.py`)
Tests all backend API functionality including:
- **Server Health**: Basic server connectivity and health checks
- **API Documentation**: Swagger UI and OpenAPI documentation
- **Authentication**: Login, token generation, and protected endpoints
- **CRUD Operations**: Create, Read, Update, Delete for all entities
- **Error Handling**: Validation, 404 errors, and error responses
- **Performance**: Response times and API performance metrics

**Usage:**
```bash
cd backend/tests
python test_backend.py --url http://127.0.0.1:8000
```

### 3. Database Testing (`test_database.py`)
Tests all database functionality including:
- **Connection**: Database connectivity and basic operations
- **Table Structure**: Schema validation and table existence
- **Data Integrity**: Foreign key constraints and data consistency
- **CRUD Operations**: Database-level create, read, update, delete
- **Relationships**: Foreign key relationships and cascade operations
- **Performance**: Query performance and optimization
- **Transactions**: Transaction handling and rollback capabilities

**Usage:**
```bash
cd backend/tests
python test_database.py
```

### 4. End-to-End Testing (`test_e2e.py`)
Tests complete user workflows including:
- **Server Management**: Automatic backend and frontend server startup
- **Authentication Flow**: Complete login and session management
- **Crew Management**: Full crew lifecycle (create, read, update, delete)
- **Flight Management**: Complete flight management workflow
- **Roster Assignment**: Crew-flight assignment and management
- **Disruption Management**: Disruption creation and handling
- **Data Consistency**: Cross-system data validation
- **Integration**: Frontend-backend integration testing

**Usage:**
```bash
cd backend/tests
python test_e2e.py
```

### 5. Disruption Testing (`test_disruptions.py`)
Tests disruption management and handling including:
- **Crew Illness**: Sick leave and replacement crew assignment
- **Weather Delays**: Weather-related flight delays and impacts
- **Aircraft Maintenance**: Maintenance issues and aircraft changes
- **Scheduling Conflicts**: Double booking and conflict resolution
- **Airport Closures**: Airport closure impacts and alternatives
- **Impact Analysis**: Disruption cascading effects and analysis
- **Resolution Workflow**: Step-by-step disruption resolution
- **Notification System**: Alert and notification mechanisms
- **Data Consistency**: Disruption data validation and integrity

**Usage:**
```bash
cd backend/tests
python test_disruptions.py --url http://127.0.0.1:8000
```

### 6. AI and Stress Testing (`test_ai_stress.py`)
Tests AI chatbot functionality and system stress testing including:
- **AI Chatbot**: Basic functionality and query processing
- **Context Awareness**: Conversation memory and context maintenance
- **Disruption Handling**: AI-powered disruption management
- **Backend-Frontend Connection**: CORS and API accessibility
- **Concurrent Requests**: System performance under load
- **Memory Usage**: Sustained load testing and memory management
- **Database Performance**: Database performance under concurrent load
- **Error Handling**: Error handling and recovery under stress

**Usage:**
```bash
cd backend/tests
python test_ai_stress.py --url http://127.0.0.1:8000 --concurrent-requests 100
```

## 🚀 Master Test Runner (`run_all_tests.py`)

The master test runner executes all test suites and generates comprehensive reports:

**Usage:**
```bash
# Run all test suites
cd backend/tests
python run_all_tests.py

# Run specific test suites
python run_all_tests.py --suites frontend backend database

# Custom output file
python run_all_tests.py --output my_test_report.json
```

## 📊 Test Results and Reports

Each test suite generates detailed JSON reports with:
- **Test Results**: Individual test pass/fail status
- **Performance Metrics**: Response times and performance data
- **Error Details**: Detailed error messages and stack traces
- **Recommendations**: Suggestions for improvements
- **Summary Statistics**: Overall success rates and metrics

### Report Files:
- `frontend_test_results.json`
- `backend_test_results.json`
- `database_test_results.json`
- `e2e_test_results.json`
- `disruption_test_results.json`
- `ai_stress_test_results.json`
- `comprehensive_test_report.json` (Master report)

## 🔧 Prerequisites

### System Requirements:
- Python 3.8+
- Node.js 16+ (for frontend tests)
- PostgreSQL database
- Backend server running on port 8000
- Frontend server running on port 5173 (for E2E tests)

### Python Dependencies:
```bash
pip install requests sqlalchemy psycopg2-binary
```

### Frontend Dependencies:
```bash
cd frontend
npm install
```

## 🎯 Test Execution Strategy

### 1. Development Testing
Run individual test suites during development:
```bash
# Test specific functionality
python test_backend.py
python test_database.py
```

### 2. Integration Testing
Run E2E tests to verify system integration:
```bash
python test_e2e.py
```

### 3. Pre-Production Testing
Run all tests before deployment:
```bash
python run_all_tests.py
```

### 4. Performance Testing
Run stress tests to validate system performance:
```bash
python test_ai_stress.py --concurrent-requests 200
```

## 📈 Success Criteria

### Individual Test Suites:
- **Frontend**: 80%+ component tests pass
- **Backend**: 90%+ API tests pass
- **Database**: 95%+ data integrity tests pass
- **E2E**: 85%+ workflow tests pass
- **Disruptions**: 90%+ disruption scenarios pass
- **AI/Stress**: 80%+ performance tests pass

### Overall System:
- **Master Test Suite**: 85%+ overall success rate
- **Performance**: <2s average response time
- **Concurrent Load**: 90%+ success rate under load
- **Error Handling**: 95%+ correct error responses

## 🐛 Troubleshooting

### Common Issues:

1. **Server Not Running**
   ```bash
   # Start backend server
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   
   # Start frontend server
   cd frontend
   npm run dev
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connection
   python scripts/create_database.py --test-connection
   ```

3. **Authentication Failures**
   - Ensure test users exist in database
   - Check password hashing configuration
   - Verify JWT token generation

4. **Frontend Build Issues**
   ```bash
   # Clean and rebuild
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

## 📝 Customization

### Adding New Tests:
1. Create new test file in `backend/tests/`
2. Follow existing test structure and patterns
3. Add to master test runner in `run_all_tests.py`
4. Update this README with new test documentation

### Modifying Test Parameters:
- **Concurrent Requests**: Modify `num_requests` parameter
- **Timeouts**: Adjust timeout values in test functions
- **Test Data**: Update test data in individual test files
- **Success Criteria**: Modify success rate thresholds

## 🔍 Test Data Management

### Test Data Creation:
- Tests create temporary data for validation
- All test data is cleaned up after execution
- Use realistic data that matches production scenarios

### Data Isolation:
- Each test suite uses isolated test data
- Tests don't interfere with each other
- Database is reset between test suites if needed

## 📞 Support

For issues with the testing framework:
1. Check test logs and error messages
2. Verify system prerequisites are met
3. Review individual test result files
4. Check database and server connectivity
5. Consult this documentation for troubleshooting

## 🎉 Success!

When all tests pass, your AeroRhythm POC is ready for:
- ✅ Production deployment
- ✅ User acceptance testing
- ✅ Performance validation
- ✅ Security verification
- ✅ Business stakeholder demonstration

The comprehensive testing suite ensures your crew rostering system is robust, reliable, and ready for real-world operations! 🚀
