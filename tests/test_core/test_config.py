from core.config import settings 


def test_settings():
    print(f'Project name: {settings.PROJECT_NAME}')
    print(f'Secret key: {settings.SECRET_KEY}')
    print(f'Api: {settings.API_V1_STR}')
    

    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES,int) 
    print('Config is ok!')
def test_config_integrity():
    # 1. Check required fields (They shouldn't be empty strings)
    assert settings.PROJECT_NAME != ""
    assert settings.SECRET_KEY != ""
    
    # 2. Check types (Pydantic does this, but it's good to verify)
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    
    # 3. Check API version format (Should start with /)
    assert settings.API_V1_STR.startswith("/")
    
    print("✅ All Configuration Integrity checks passed!") 

if __name__ == '__main__':
    test_settings() 
