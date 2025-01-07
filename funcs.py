from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ChromeOptions, Keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from datetime import datetime, timedelta,timezone

def element_exists(driver:webdriver, by:By, ref:str, time=4, refresh=False):
    ret = False
    try:    # Check si existen más opciones que las del inicio - hacer click en caso de existir
        ret = WebDriverWait(driver, time).until(EC.presence_of_element_located((by,ref)))
        if refresh == True:
            driver.refresh()
        try:
            ret = WebDriverWait(driver, time).until(EC.presence_of_element_located((by,ref)))
        except :
            pass
    except TimeoutException:
        pass
    return ret

def get_reels(driver):
    with open("perfiles.txt") as f:
        users_raw = f.readlines()
        users = [x.strip() for x in users_raw]
    final_results = []
    for user in users:
        driver.get("https://www.instagram.com/" + user)
        time.sleep(4)
        boton_reels = element_exists(driver,By.XPATH, f'//a[@href="/{user}/reels/"]')
        if boton_reels:
            boton_reels.click()
            time.sleep(4)
        
        visualizations = driver.find_elements(By.XPATH, f"//a[starts-with(@href, '/{user}/reel/') and not(.//*[local-name()='svg'][@aria-label='Pinned post icon'])]")

        visualizations = visualizations[:5]

        temp_results = [(user, viz.text, viz.get_attribute('href')) for viz in visualizations]

        final_results.extend(temp_results)
    
    lista_reels = [x[2] for x in final_results]

    fechas = []

    for index, reel in enumerate(lista_reels):
        driver.get(reel)
        fecha = element_exists(driver, By.XPATH, "//time[@datetime]")
        fecha = fecha.get_attribute('datetime')
        final_results[index] = final_results[index] + (fecha,)
        fechas.append(fecha)

    df = pd.DataFrame(final_results, columns=["usuario", "visualizaciones", "url_reel","fechas"])
    df['fechas'] = pd.to_datetime(df['fechas'])
    ahora = datetime.now(timezone.utc)
    umbral = ahora - timedelta(days=2)
    df_filtrado = df[df['fechas'] > umbral]
    df_filtrado.to_csv("reels.csv", index=False)
    return df_filtrado



def login(username, password):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.instagram.com/")

    input_email = element_exists(driver,By.XPATH,'//input[@name="username"]')
    input_email.send_keys(username)

    input_pass = element_exists(driver,By.XPATH,'//input[@name="password"]')
    input_pass.send_keys(password)

    input_pass.send_keys(Keys.ENTER)

    time.sleep(5)
    no_guardar = element_exists(driver,By.XPATH,'//div[@role="button"]')   
    if no_guardar:
        no_guardar.click()
    
    return driver