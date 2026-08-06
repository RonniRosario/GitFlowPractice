import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


RUTA_INDEX = "file:///C:/Users/ronni/onedrive/escritorio/itla/c5/p3/tarea4/gitflowpractice/index.html"

@pytest.fixture
def driver():
    """Configuración inicial del WebDriver para Microsoft Edge"""
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(options=options)
    driver.maximize_window()
    
    os.makedirs("capturas", exist_ok=True)
    
    yield driver
    
    time.sleep(2)
    driver.quit()

@pytest.fixture(autouse=True)
def clean_local_storage(driver):
    """Limpia el almacenamiento local antes de cada prueba (Aislamiento de pruebas)"""
    driver.get(RUTA_INDEX)
    driver.execute_script("window.localStorage.clear();")
    driver.refresh()
    time.sleep(1)


def test_stock7_camino_feliz(driver):
    """Prueba de Camino Feliz: Creación exitosa de un producto"""
    # 1. Abrir modal
    driver.find_element(By.ID, "btn-add-product").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    time.sleep(1) 
    
    # 2. Llenar formulario
    driver.find_element(By.ID, "productName").send_keys("Monitor UltraWide")
    time.sleep(1)
    
    Select(driver.find_element(By.ID, "productCategory")).select_by_value("Electronics")
    time.sleep(1)
    
    driver.find_element(By.ID, "productPrice").send_keys("350.50")
    time.sleep(1)
    
    # 3. Guardar
    driver.find_element(By.ID, "btn-save-product").click()
    
    # 4. Validar que la alerta de éxito aparezca y el modal se cierre
    alerta = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock7_camino_feliz.png")
    
    tabla = driver.find_element(By.ID, "product-table-body").text
    assert "Monitor UltraWide" in tabla
    assert "Product added successfully" in alerta.text

def test_stock7_prueba_negativa(driver):
    """Prueba Negativa: Intento de crear un producto con nombre duplicado"""
    # 1. Crear el primer producto mediante JavaScript para preparar el entorno rápidamente
    driver.execute_script("""
        let products = [{id: '123', name: 'Laptop', category: 'Electronics', price: 1000}];
        localStorage.setItem('stockflow_products', JSON.stringify(products));
    """)
    driver.refresh()
    time.sleep(1)
    
    # 2. Intentar crear otro producto con el mismo nombre ("Laptop")
    driver.find_element(By.ID, "btn-add-product").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    
    driver.find_element(By.ID, "productName").send_keys("Laptop")
    Select(driver.find_element(By.ID, "productCategory")).select_by_value("Electronics")
    driver.find_element(By.ID, "productPrice").send_keys("1500.00")
    time.sleep(1)
    
    driver.find_element(By.ID, "btn-save-product").click()
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock7_prueba_negativa.png")
    
    # 3. Validar que el formulario no se envió (el modal sigue abierto) y muestra el error
    modal = driver.find_element(By.ID, "productModal")
    feedback = driver.find_element(By.XPATH, "//input[@id='productName']/following-sibling::div[@class='invalid-feedback']")
    
    assert modal.is_displayed()
    assert "A product with this name already exists" in feedback.text

def test_stock7_prueba_limites(driver):
    """Prueba de Límites: Precio en 0 o negativo"""
    driver.find_element(By.ID, "btn-add-product").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    
    # Llenar datos correctos pero con precio 0 
    driver.find_element(By.ID, "productName").send_keys("Teclado Mecánico")
    Select(driver.find_element(By.ID, "productCategory")).select_by_value("Electronics")
    
    input_precio = driver.find_element(By.ID, "productPrice")
    input_precio.send_keys("0") 
    time.sleep(1.5) 
    
    driver.find_element(By.ID, "btn-save-product").click()
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock7_prueba_limites.png")
    
    formulario = driver.find_element(By.ID, "productForm")
    clases_formulario = formulario.get_attribute("class")
    
    assert "was-validated" in clases_formulario
    contador = driver.find_element(By.ID, "product-counter").text
    assert "0 products" in contador