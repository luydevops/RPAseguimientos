import time
from SeleniumBot import SeleniumBot
from selenium.webdriver.common.by import By
import csv
import os
from datetime import datetime
import re

class RpaBot:
    def __init__(self):
        """Constructor que inicializa el bot de Selenium."""
        self.bot = SeleniumBot()

    def login(self, username, password):
        """Función para iniciar sesión en la página."""
        self.bot.abrir_pagina("https://seguimientos.territorios.mx/inicio")

        # Buscar y llenar el campo de usuario
        campo_usuario = self.bot.buscar_elemento("#input_login_username", By.CSS_SELECTOR)
        if campo_usuario:
            campo_usuario.send_keys(username)
        else:
            print("No se encontró el campo de usuario.")

        # Buscar y llenar el campo de contraseña
        campo_password = self.bot.buscar_elemento("#input_login_password", By.CSS_SELECTOR)
        if campo_password:
            campo_password.send_keys(password)
        else:
            print("No se encontró el campo de contraseña.")

        # Buscar y hacer clic en el botón de inicio de sesión
        boton_login = self.bot.buscar_elemento("button", By.CSS_SELECTOR)
        if boton_login:
            boton_login.click()
        else:
            print("No se encontró el botón de inicio de sesión.")

    def navegacionTabla(self):
        """Navega hasta la tabla y captura las URLs de los enlaces <a class="azul"> dentro de cada fila, regresa a la tabla original después de cada interacción."""
        # Hacer clic en el segundo enlace para llegar a la tabla
        self.bot.esperar_elemento("a:nth-of-type(2)", By.CSS_SELECTOR, tiempo_espera=1, max_intentos=10)
        boton_tabla = self.bot.buscar_elemento("a:nth-of-type(2)", By.CSS_SELECTOR)
        if boton_tabla:
            boton_tabla.click()
            print("Se hizo clic en el botón de navegación a la tabla.")
        else:
            print("No se encontró el botón para navegar a la tabla.")
            return

        # Validar si existe el botón "Asignaciones" con reintentos
        boton_asignaciones = self.bot.esperar_elemento("input[value='Asignaciones']", By.CSS_SELECTOR, tiempo_espera=1,
                                                       max_intentos=10)
        if boton_asignaciones:
            print("Botón 'Asignaciones' encontrado.")
            boton_asignaciones.click()
        else:
            print("No se encontró el botón 'Asignaciones' después de varios intentos.")
            return

        self.bot.esperar_elemento("a.azul", By.CSS_SELECTOR, tiempo_espera=1, max_intentos=10)

        # Contar cuántos enlaces 'a.azul' existen en las filas
        filas = self.bot.buscar_elementos("a.azul", By.CSS_SELECTOR)
        total_filas = len(filas)
        print(f"Total de filas encontradas: {total_filas}")

        if total_filas > 0:
            # Iterar sobre cada fila y capturar el enlace 'a.azul'
            for i in range(1, total_filas + 1):
                selector = f"table > tbody > tr:nth-child({i}) > td.tabla_reporte.col_19 > a.azul"
                elemento = self.bot.esperar_elemento(selector, By.CSS_SELECTOR, tiempo_espera=1, max_intentos=10)

                if elemento:
                    print(f"Procesando enlace en la fila {i} elemento: {selector} ")
                    elemento.click()  # Hacer clic en el enlace

                    # Capturar información de la página (si es necesario)
                    self.bot.esperar_elemento("a[title='Ver datos del representante']", By.CSS_SELECTOR, tiempo_espera=1, max_intentos=6)
                    # Contar cuántos enlaces 'a[title='Ver datos del representante']' existen en las filas
                    filas_estado = self.bot.buscar_elementos("a[title='Ver datos del representante']", By.CSS_SELECTOR)
                    total_estado_filas = len(filas_estado)
                    if self.valida_datos_municipio(i, total_estado_filas):
                        print(f"Municipio {i} ya procesado, saltando...")
                        # Regresar a la tabla haciendo clic en el botón 'Asignaciones'
                        boton_asignaciones = self.bot.esperar_elemento("input#error_formulario_boton", By.CSS_SELECTOR,
                                                                       tiempo_espera=1, max_intentos=6)
                        if boton_asignaciones:
                            print("Regresando a la tabla original.")
                            boton_asignaciones.click()
                        continue  # SALTAR ESTA ITERACIÓN Y PASAR AL SIGUIENTE MUNICIPIO
                    print(f"Total de filas estado encontradas: {total_estado_filas}")
                    if total_estado_filas > 0:
                        # Iterar sobre cada fila y capturar el enlace 'a[title='Ver datos del representante']'
                        for a in range(1, total_estado_filas + 1):
                            selector_estado = f"table > tbody > tr:nth-child({a}) > td.tabla_reporte.col_7 > a:nth-child(1)"
                            print(selector_estado)
                            print(f"vas en el registro {a}/{total_estado_filas}")
                            elemento_estado = self.bot.esperar_elemento(selector_estado, By.CSS_SELECTOR,
                                                                        tiempo_espera=1, max_intentos=10)
                            # print(elemento_estado)
                            if elemento_estado:
                                self.captura_datos(selector_estado, a)
                                # time.sleep(10)  # Esperar un poco mientras se recarga la tabla
                            else:
                                print(f"el elemento {elemento_estado} no se encontrado.")

                            self.bot.scroll_down(30)

                    # Regresar a la tabla haciendo clic en el botón 'Asignaciones'
                    boton_asignaciones = self.bot.esperar_elemento("input#error_formulario_boton", By.CSS_SELECTOR,
                                                                   tiempo_espera=1, max_intentos=6)
                    if boton_asignaciones:
                        print("Regresando a la tabla original.")
                        boton_asignaciones.click()
                        time.sleep(2)  # Esperar un poco mientras se recarga la tabla
                    else:
                        print("No se encontró el botón 'Asignaciones' para regresar a la tabla.")
                else:
                    print(f"No se encontró el enlace 'a.azul' en la fila {i}")
        else:
            print("No se encontraron filas con enlaces 'a.azul'.")

    def captura_datos(self, btn, fila=None):
        """Captura los datos de la modal y los guarda en un archivo CSV."""

        # Ahora vamos a capturar los datos de la modal
        datos = {}

        # Capturar cargo
        cargo = self.bot.buscar_elemento(f"table > tbody > tr:nth-child({fila}) > td.tabla_reporte.col_2", By.CSS_SELECTOR)
        datos["cargo"] = cargo.get_attribute("innerText").replace("\n", " ").encode("latin1").decode("utf-8") if cargo else "No disponible"

        # Capturar seccion
        seccion = self.bot.buscar_elemento(f"table > tbody > tr:nth-child({fila}) > td.tabla_reporte.col_3", By.CSS_SELECTOR)
        datos["seccion"] = seccion.get_attribute("innerText").replace("\n", " ").encode("latin1").decode("utf-8") if seccion else "No disponible"

        # Capturar casilla
        casilla = self.bot.buscar_elemento(f"table > tbody > tr:nth-child({fila}) > td.tabla_reporte.col_4", By.CSS_SELECTOR)
        datos["casilla"] = casilla.get_attribute("innerText").replace("\n", " ").encode("latin1").decode("utf-8") if casilla else "No disponible"

        # Capturar municipio
        municipio = self.bot.buscar_elemento("div.principal_barra_apps h3", By.CSS_SELECTOR)
        datos["municipio"] = municipio.get_attribute("innerText").replace("\n", " ").encode("latin1").decode("utf-8") if municipio else "No disponible"

        # Hacer clic en el botón "Ver datos del representante" para abrir la modal
        boton_ver_datos = self.bot.buscar_elemento(btn, By.CSS_SELECTOR)
        # time.sleep(2)  # Esperar un poco mientras se recarga la tabla
        if boton_ver_datos:
            boton_ver_datos.click()
            print("Se hizo clic en el botón 'Ver datos del representante'.")
        else:
            print("No se encontró el botón 'Ver datos del representante'.")
            return

        self.bot.esperar_elemento(".box-front .encabezado p", By.CSS_SELECTOR, tiempo_espera=1, max_intentos=10)

        # Capturar la clave de elector
        clave_elector = self.bot.buscar_elemento(".cve_ife h4", By.CSS_SELECTOR)
        datos["clave_elector"] = clave_elector.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if clave_elector else "No disponible"

        # Capturar el nombre
        nombre = self.bot.buscar_elemento(".nombre h3", By.CSS_SELECTOR)
        datos["nombre"] = nombre.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if nombre else "No disponible"

        # Capturar la sesión
        session = self.bot.buscar_elemento(".box-front .encabezado em", By.CSS_SELECTOR)
        datos["session"] = session.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if session else "No disponible"

        # Capturar el representante
        representante = self.bot.buscar_elemento(".box-front h2", By.CSS_SELECTOR)
        datos["representante"] = representante.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if representante else "No disponible"

        # Capturar el genero
        genero = self.bot.buscar_elemento(".nombre em", By.CSS_SELECTOR)
        datos["genero"] = genero.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if genero else "No disponible"

        # Capturar el estado
        estado = self.bot.buscar_elemento(".box-front .encabezado p", By.CSS_SELECTOR)
        datos["estado provincia"] = estado.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if estado else "No disponible"

        # Capturar teléfono fijo
        telefono_fijo = self.bot.buscar_elemento(".telefono_fijo h4", By.CSS_SELECTOR)
        datos["telefono_fijo"] = telefono_fijo.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if telefono_fijo else "No disponible"

        # Capturar teléfono móvil
        telefono_movil = self.bot.buscar_elemento(".telefono_movil h4", By.CSS_SELECTOR)
        datos["telefono_movil"] = telefono_movil.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if telefono_movil else "No disponible"

        # Capturar email
        email = self.bot.buscar_elemento(".email h4", By.CSS_SELECTOR)
        datos["email"] = email.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if email else "No disponible"

        # Capturar antecedentes
        antecedentes = self.bot.buscar_elemento(".origen p:nth-of-type(2)", By.CSS_SELECTOR)
        datos["antecedentes"] = antecedentes.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if antecedentes else "No disponible"

        # Capturar status 2025
        status_2025 = self.bot.buscar_elemento(".status p:nth-of-type(2)", By.CSS_SELECTOR)
        datos["status_2025"] = status_2025.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if status_2025 else "No disponible"

        # Capturar domicilio
        domicilio = self.bot.buscar_elemento("span.observ", By.CSS_SELECTOR)
        datos["domicilio"] = domicilio.get_attribute("innerText").replace("\n", " ").encode("utf-8", "ignore").decode("utf-8") if domicilio else "No disponible"

        # Imprimir los datos capturados
        print("Datos capturados:")
        for clave, valor in datos.items():
            print(f"{clave}: {valor}")

        # Extraer el número con regex
        match = re.search(r'Dtto\s*(\d+)', municipio.text)
        numero_municipio = match.group(1)
        # Llamar a la función para guardar los datos en el archivo CSV
        self.cargar_datos_csv(datos, numero_municipio)

        boton_close = self.bot.esperar_elemento("input.error_formulario_boton", By.CSS_SELECTOR, tiempo_espera=1, max_intentos=6)
        if boton_close:
            print("Regresando a la tabla estado.")
            # Inyectar CSS para modificar el z-index
            script_css = """
                            var elementoDatosCandidato = document.querySelector('.datos_candidato');
                            if (elementoDatosCandidato) {
                                elementoDatosCandidato.style.zIndex = '0';
                            }
                            var botonCerrar = document.querySelector('input.error_formulario_boton');
                            if (botonCerrar) {
                                botonCerrar.style.zIndex = '1';
                                botonCerrar.style.position = 'relative'; // Importante para que z-index funcione
                            }
                        """
            self.bot.driver.execute_script(script_css)
            time.sleep(1)  # Dar tiempo para que los estilos se apliquen
            boton_close.click()


    def cargar_datos_csv(self, datos, municipio=None):
        """Guarda los datos capturados en un archivo CSV dentro de una carpeta con la fecha y opcionalmente por municipio."""

        # Obtener la fecha y hora actual en el formato requerido (DD_MM_YYYY)
        fecha_hora = datetime.now().strftime("%d_%m_%Y")

        # Definir la carpeta base con la fecha
        carpeta = fecha_hora

        # Si municipio tiene valor, agregarlo a la ruta
        if municipio:
            carpeta = os.path.join(carpeta, municipio)

        # Crear la carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)

        # Definir la ruta completa del archivo CSV
        archivo_csv = os.path.join(carpeta, "datos_representante.csv")

        # Comprobar si el archivo existe para saber si se deben agregar los encabezados
        archivo_existe = os.path.isfile(archivo_csv)

        # Abrir el archivo en modo de añadir (append)
        with open(archivo_csv, mode='a', newline='', encoding='utf-8-sig') as archivo:
            escritor_csv = csv.DictWriter(archivo, fieldnames=datos.keys())

            # Si el archivo no existe, escribir los encabezados (primera vez que se ejecuta)
            if not archivo_existe:
                escritor_csv.writeheader()

            # Escribir los datos en una nueva fila
            escritor_csv.writerow(datos)
            print(f"Datos guardados en {archivo_csv}")

    def valida_datos_municipio(self, municipio, num_filas_esperadas):
        """Verifica si existe la carpeta del municipio, su CSV y si la cantidad de filas coincide con lo esperado.

        Retorna True si debe saltarse este municipio (hacer break).
        Retorna False si el municipio debe procesarse.
        """

        # Obtener la fecha actual en formato DD_MM_YYYY
        fecha_hora = datetime.now().strftime("%d_%m_%Y")

        # Definir la ruta de la carpeta del municipio
        carpeta_municipio = os.path.join(fecha_hora, str(municipio))  # Convertir a str por si es numérico
        archivo_csv = os.path.join(carpeta_municipio, "datos_representante.csv")

        # Verificar si la carpeta o el archivo no existen
        if not os.path.exists(carpeta_municipio) or not os.path.isfile(archivo_csv):
            return False  # No existe, se debe procesar

        # Contar la cantidad de filas en el CSV
        with open(archivo_csv, mode='r', newline='', encoding='utf-8-sig') as archivo:
            lector_csv = csv.reader(archivo)
            filas = list(lector_csv)  # Convertimos a lista para contar
            num_filas_actuales = len(filas) - 1  # Restamos 1 para excluir el encabezado

        # Si el número de filas coincide con el esperado, se debe saltar el municipio
        return num_filas_actuales >= num_filas_esperadas

    def cerrar(self):
        """Cierra el navegador."""
        self.bot.cerrar()


if __name__ == "__main__":
    rpa = RpaBot()
    rpa.login("dievil", "jv79USrvF")
    rpa.navegacionTabla()

    rpa.cerrar()
