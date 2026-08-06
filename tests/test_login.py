import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


RUTA_LOGIN = "file:///C:/Users/ronni/onedrive/escritorio/itla/c5/p3/tarea4/gitflowpractice/login.html"

@pytest.fixture
def driver():

    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(options=options)
    driver.maximize_window()
    
    os.makedirs("capturas", exist_ok=True)
    
    yield driver
    
    
    time.sleep(2)
    driver.quit()



def test_login_camino_feliz(driver):
    """Prueba de Camino Feliz: Credenciales correctas"""
    driver.get(RUTA_LOGIN)
    time.sleep(2)  
    
    driver.find_element(By.ID, "username").send_keys("admin")
    time.sleep(1) 
    
    driver.find_element(By.ID, "password").send_keys("admin123")
    time.sleep(1)  
    
    driver.find_element(By.ID, "btn-login").click()
    
    WebDriverWait(driver, 5).until(EC.url_contains("index.html"))
    time.sleep(2) 
    
    driver.save_screenshot("capturas/test_login_camino_feliz.png")
    assert "index.html" in driver.current_url

def test_login_prueba_negativa(driver):
    """Prueba Negativa: Credenciales incorrectas"""
    driver.get(RUTA_LOGIN)
    time.sleep(1)
    
    driver.find_element(By.ID, "username").send_keys("admin")
    time.sleep(1)
    
    driver.find_element(By.ID, "password").send_keys("clave_equivocada")
    time.sleep(1)
    
    driver.find_element(By.ID, "btn-login").click()
    
    alerta = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "login-alert"))
    )
    
    time.sleep(2)
    
    driver.save_screenshot("capturas/test_login_prueba_negativa.png")
    assert alerta.is_displayed()
    assert "error" in alerta.text.lower() or "incorrect" in alerta.text.lower()

def test_login_prueba_limites(driver):
    """Prueba de Límites: Formulario vacío"""
    driver.get(RUTA_LOGIN)
    time.sleep(2)
    
    driver.find_element(By.ID, "btn-login").click()
    
    time.sleep(2)
    
    driver.save_screenshot("capturas/test_login_prueba_limites.png")
    assert "index.html" not in driver.current_url