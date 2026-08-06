import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
def setup_data(driver):
    """Inyecta dos productos inicialmente"""
    driver.get(RUTA_INDEX)
    driver.execute_script("""
        let products = [
            {id: '1', name: 'Auriculares Bluetooth', category: 'Electronics', price: 50.00},
            {id: '2', name: 'Mochila de Viaje', category: 'Sports & Outdoors', price: 45.00}
        ];
        localStorage.setItem('stockflow_products', JSON.stringify(products));
    """)
    driver.refresh()
    time.sleep(1) 


def test_stock10_camino_feliz(driver):
    """Prueba de Camino Feliz: Eliminación de un producto dejando otros en la tabla"""
    # 1. Identificar el botón de eliminar del primer producto (Auriculares)
    btn_eliminar = driver.find_element(By.CSS_SELECTOR, ".btn-delete[data-id='1']")
    
    
    btn_eliminar.click()
    
    # 3. Validar la alerta verde de éxito
    alerta = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock10_camino_feliz.png")
    
    # 4. Validar que los auriculares desaparecieron pero la mochila sigue ahí
    tabla = driver.find_element(By.ID, "product-table-body").text
    assert "Auriculares Bluetooth" not in tabla
    assert "Mochila de Viaje" in tabla
    assert "Product deleted successfully" in alerta.text

def test_stock10_prueba_limites(driver):
    """Prueba de Límites: Eliminar el último producto para desencadenar el estado vacío"""
    # Preparar el entorno para que solo haya 1 producto
    driver.execute_script("""
        let products = [{id: '1', name: 'Auriculares Bluetooth', category: 'Electronics', price: 50.00}];
        localStorage.setItem('stockflow_products', JSON.stringify(products));
    """)
    driver.refresh()
    time.sleep(1.5) 
    
    
    driver.find_element(By.CSS_SELECTOR, ".btn-delete[data-id='1']").click()
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock10_prueba_limites.png")
    
    
    estado_vacio = driver.find_element(By.ID, "empty-state")
    contador = driver.find_element(By.ID, "product-counter").text
    
    assert not estado_vacio.get_attribute("class").__contains__("d-none")
    assert "No products found" in estado_vacio.text
    assert "0 products" in contador

def test_stock10_prueba_negativa(driver):
    """Prueba Negativa: Intento de eliminar un registro que ya no existe en memoria"""
    
    driver.execute_script("products = [];")
    time.sleep(1.5)
    
    # Hacemos clic en el botón original que todavía está visible
    driver.find_element(By.CSS_SELECTOR, ".btn-delete[data-id='1']").click()
    
    # Validar que aparezca la alerta de peligro (danger)
    alerta = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
    )
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock10_prueba_negativa.png")
    
    assert "Unable to delete. Product not found." in alerta.text