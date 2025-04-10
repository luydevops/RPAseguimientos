from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class SeleniumBot:
    def __init__(self, driver_path=None):
        """Inicializa el WebDriver."""
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
        options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memoria en Docker
        self.driver = webdriver.Chrome(options=options) if driver_path is None else webdriver.Chrome(executable_path=driver_path, options=options)


    def abrir_pagina(self, url):
        """Abre una URL en el navegador."""
        self.driver.get(url)

    def buscar_elemento(self, selector, by=By.CSS_SELECTOR):
        """Busca un solo elemento en la página."""
        try:
            return self.driver.find_element(by, selector)
        except Exception as e:
            # print(f"Error buscando el elemento {selector}: {e}")
            print(f"Error buscando el elemento {selector}")
            return None

    def buscar_elementos(self, selector, by=By.CSS_SELECTOR):
        """Busca una lista de elementos en la página."""
        try:
            return self.driver.find_elements(by, selector)
        except Exception as e:
            print(f"Error buscando los elementos {selector}: {e}")
            return []

    def esperar_elemento(self, selector, by=By.CSS_SELECTOR, tiempo_espera=1, max_intentos=4):
        """
        Espera hasta que el elemento aparezca en la página con reintentos.

        :param selector: Selector del elemento
        :param by: Tipo de selector (CSS_SELECTOR por defecto)
        :param tiempo_espera: Tiempo entre intentos (segundos)
        :param max_intentos: Número máximo de intentos
        :return: WebElement si se encuentra, None si no se encuentra
        """
        for intento in range(max_intentos):
            elemento = self.buscar_elemento(selector, by)
            if elemento:
                return elemento
            print(
                f"Intento {intento + 1}/{max_intentos}: Elemento {selector} no encontrado, esperando {tiempo_espera} segundos...")
            time.sleep(tiempo_espera)
        print(f"Elemento {selector} no encontrado después de {max_intentos} intentos.")
        return None

    def obtener_url_actual(self):
        """Obtiene la URL actual del navegador."""
        return self.driver.current_url

    def scroll_down(self, pixels: int):
        """Realiza un scroll hacia abajo una cantidad específica de píxeles, asegurando que el contenido se actualice."""
        self.driver.execute_script(f"""
        let elemento = document.querySelector('.principal_barra_apps.print');
        if (elemento) {{
            elemento.scrollTop += {pixels};
        }}
        """)
        time.sleep(0.5)  # Pequeña espera para permitir la carga dinámica

    def scroll_to_element(self, selector: str, by=By.CSS_SELECTOR):
        """Hace scroll hasta que el elemento esté visible en pantalla."""
        elemento = self.driver.find_element(by, selector)
        self.driver.execute_script("arguments[0].scrollIntoView();", elemento)
        time.sleep(0.8)  # Da tiempo a la página para actualizar el contenido

    def cerrar(self):
        """Cierra el navegador."""
        self.driver.quit()
