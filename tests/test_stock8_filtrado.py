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
def setup_data(driver):
    """Limpia e inyecta datos de prueba antes de cada escenario"""
    driver.get(RUTA_INDEX)
    # Inyectamos 3 productos variados para poder filtrarlos
    driver.execute_script("""
        let products = [
            {id: '1', name: 'Mouse Inalámbrico', category: 'Electronics', price: 25.00},
            {id: '2', name: 'Teclado Mecánico', category: 'Electronics', price: 75.00},
            {id: '3', name: 'Libro de Programación', category: 'Books', price: 40.00}
        ];
        localStorage.setItem('stockflow_products', JSON.stringify(products));
    """)
    driver.refresh()
    time.sleep(1) 


def test_stock8_camino_feliz(driver):
    """Prueba de Camino Feliz: Filtrado exitoso por texto y categoría"""
    buscador = driver.find_element(By.ID, "search-input")
    
    # Escribir en el buscador
    buscador.send_keys("Mouse")
    time.sleep(2) # Pausa para ver cómo se filtra la tabla en vivo
    
    driver.save_screenshot("capturas/stock8_camino_feliz.png")
    
    # Validar que solo se muestra 1 producto y es el correcto
    filas = driver.find_elements(By.XPATH, "//tbody[@id='product-table-body']/tr")
    assert len(filas) == 1
    assert "Mouse Inalámbrico" in filas[0].text
    
    # Validar que el contador se actualizó
    contador = driver.find_element(By.ID, "product-counter").text
    assert "1 product" in contador

def test_stock8_prueba_negativa(driver):
    """Prueba Negativa: Búsqueda de un producto que no existe"""
    buscador = driver.find_element(By.ID, "search-input")
    
    buscador.send_keys("Laptop")
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock8_prueba_negativa.png")
    
    estado_vacio = driver.find_element(By.ID, "empty-state")
    assert not estado_vacio.get_attribute("class").__contains__("d-none")
    
    # Validar el texto del mensaje de error
    mensaje = estado_vacio.find_element(By.TAG_NAME, "h5").text
    assert "No matching products found" in mensaje

def test_stock8_prueba_limites(driver):
    """Prueba de Límites: Tolerancia a espacios en blanco extra y mayúsculas/minúsculas"""
    buscador = driver.find_element(By.ID, "search-input")
    
    buscador.send_keys("   LIBRO   ")
    time.sleep(2) 
    
    driver.save_screenshot("capturas/stock8_prueba_limites.png")
    
    filas = driver.find_elements(By.XPATH, "//tbody[@id='product-table-body']/tr")
    assert len(filas) == 1
    assert "Libro de Programación" in filas[0].text