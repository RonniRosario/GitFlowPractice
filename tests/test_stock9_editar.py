import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


RUTA_INDEX = "file:///C:/Users/ronni/OneDrive/escritorio/ITLA/C5/P3/TAREA4/GitFlowPractice/index.html"

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
def setup_data(driver):
    """Inyecta dos productos para realizar pruebas de edición y duplicidad"""
    driver.get(RUTA_INDEX)
    driver.execute_script("""
        let products = [
            {id: '1', name: 'Monitor LG', category: 'Electronics', price: 200.00},
            {id: '2', name: 'Silla Ergonomica', category: 'Home & Kitchen', price: 150.00}
        ];
        localStorage.setItem('stockflow_products', JSON.stringify(products));
    """)
    driver.refresh()
    time.sleep(1) 


def test_stock9_camino_feliz(driver):
    """Prueba de Camino Feliz: Edición exitosa de un producto"""
    btn_editar = driver.find_element(By.CSS_SELECTOR, ".btn-edit[data-id='1']")
    btn_editar.click()
    
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    time.sleep(1.5) 
    
    # 2. Modificar el precio
    input_precio = driver.find_element(By.ID, "productPrice")
    input_precio.clear()
    time.sleep(0.5)
    input_precio.send_keys("250.99")
    time.sleep(1) # Pausa para ver el nuevo precio
    
    # 3. Guardar cambios
    driver.find_element(By.ID, "btn-save-product").click()
    
    # 4. Validar la alerta y la actualización en la tabla
    alerta = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock9_camino_feliz.png")
    
    tabla = driver.find_element(By.ID, "product-table-body").text
    assert "250.99" in tabla
    assert "Product updated successfully" in alerta.text

def test_stock9_prueba_negativa(driver):
    """Prueba Negativa: Intento de guardar un producto con el nombre en blanco"""
    # 1. Abrir modal de edición
    driver.find_element(By.CSS_SELECTOR, ".btn-edit[data-id='1']").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    time.sleep(1)
    

    input_nombre = driver.find_element(By.ID, "productName")
    input_nombre.clear()
    time.sleep(1.5) 
    

    driver.find_element(By.ID, "btn-save-product").click()
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock9_prueba_negativa.png")
    
    # 4. Validar que el formulario fue marcado como inválido y el modal sigue abierto
    formulario = driver.find_element(By.ID, "productForm")
    modal = driver.find_element(By.ID, "productModal")
    
    assert "was-validated" in formulario.get_attribute("class")
    assert modal.is_displayed()

def test_stock9_prueba_limites(driver):
    """Prueba de Límites: Intento de cambiar el nombre a uno que ya existe en otro registro"""
    # 1. Abrir modal de edición del "Monitor LG" (id: 1)
    driver.find_element(By.CSS_SELECTOR, ".btn-edit[data-id='1']").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "productModal")))
    time.sleep(1)
    
    # 2. Cambiar el nombre por "Silla Ergonomica" (que pertenece al id: 2)
    input_nombre = driver.find_element(By.ID, "productName")
    input_nombre.clear()
    input_nombre.send_keys("Silla Ergonomica")
    time.sleep(1.5) # Pausa para ver el nombre conflictivo
    
    # 3. Intentar guardar
    driver.find_element(By.ID, "btn-save-product").click()
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock9_prueba_limites.png")
    
    # 4. Validar el mensaje de error personalizado
    feedback = driver.find_element(By.XPATH, "//input[@id='productName']/following-sibling::div[@class='invalid-feedback']")
    assert "A product with this name already exists" in feedback.text