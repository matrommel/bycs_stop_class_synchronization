import os
import configparser
import csv
import logging
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

# TensorFlow-Logstufe auf ERROR setzen
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Konfiguration für Logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def create_webdriver(headless):
    options = Options()
    if headless:
        # Verwende den neuen Headless-Modus, falls verfügbar
        options.add_argument("--headless=new")
        # Alternativ: Bei älteren Versionen kann "--headless" verwendet werden
        # options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Fenstergröße definieren (wichtig im Headless-Modus)
        options.add_argument('window-size=1920x1080')
    return webdriver.Chrome(options=options)

def login(driver, username, password, waittime):
    logging.info("Navigiere zur Login-Seite...")
    driver.get("https://lernplattform.mebis.bycs.de/login/index.php")
    wait = WebDriverWait(driver, waittime)
    
    wait.until(EC.visibility_of_element_located((By.ID, "input-username"))).send_keys(username)
    logging.info("Benutzername eingegeben...")
    driver.find_element(By.ID, "input-password").send_keys(password)
    logging.info("Passwort eingegeben...")
    driver.find_element(By.ID, "button-do-log-in").click()
    logging.info("Login-Versuch gestartet...")

def read_course_ids_from_csv(file_path):
    course_ids = set()
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    course_ids.add(row[0])  # Annahme: Die CourseID ist in der ersten Spalte
    return course_ids

def write_course_ids_to_csv(file_path, course_ids):
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for course_id in course_ids:
            writer.writerow([course_id])

def extract_classes(driver, course_id, waittime):
    classes = []
    enrol_url = f'https://lernplattform.mebis.bycs.de/enrol/instances.php?id={course_id}'
    logging.info(f"Navigiere zur Einschreibeseite für Kurs-ID {course_id}...")
    driver.get(enrol_url)

    # Verwende WebDriverWait, um sicherzustellen, dass die benötigten Elemente vorhanden sind
    try:
        wait = WebDriverWait(driver, waittime)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a[href*='enrol/editinstance.php?courseid=']")))
    except TimeoutException:
        logging.warning(f"Keine Klassenlinks gefunden für Kurs-ID {course_id}.")
        return classes

    class_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='enrol/editinstance.php?courseid=']")
    logging.info(f"Gefundene Klassenlinks für Kurs-ID {course_id}: {len(class_links)}")
    for link in class_links:
        href = link.get_attribute("href")
        if href:
            classes.append(href)
    
    return classes

def process_classes(driver, classes, waittime):
    processed_course_ids = set()  # Set für erfolgreich bearbeitete Kurs-IDs
    wait = WebDriverWait(driver, waittime)
    
    for class_url in classes:
        logging.info(f"Verarbeite Klasse: {class_url}")
        driver.get(class_url)
    
        # Warten, bis die Seite geladen ist (hier zusätzlich als Fallback ein kleiner Sleep)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            logging.warning(f"Seite nicht vollständig geladen für {class_url}")
            continue

        # Klicke auf "Ausführliche Eingabe"
        try:
            detailed_input_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a#scrolltop"))
            )
            detailed_input_button.click()
            logging.info("Klick auf 'Ausführliche Eingabe' erfolgreich.")
        except TimeoutException:
            logging.warning(f"Button 'Ausführliche Eingabe' nicht gefunden für {class_url}")
            continue

        # Wähle "Nein" im Select-Element aus
        try:
            select_element = wait.until(
                EC.presence_of_element_located((By.ID, "id_customint3"))
            )
            # Setze den Wert mit JavaScript und triggere das change-Event
            driver.execute_script("arguments[0].value = '0';", select_element)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", select_element)
            logging.info("Auswahl 'Nein' erfolgreich getroffen.")
        except TimeoutException:
            logging.warning(f"Dropdown für 'customint3' nicht gefunden für {class_url}")
            continue

        # Bestätige mit "Änderungen speichern"
        try:
            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "id_submitbutton")))
            submit_button.click()
            logging.info("Änderungen gespeichert.")
            # Extrahiere die Kurs-ID aus der URL mithilfe eines regulären Ausdrucks
            match = re.search(r'id=(\d+)', class_url)
            if match:
                processed_course_ids.add(match.group(1))
            else:
                logging.warning(f"Kurs-ID konnte nicht extrahiert werden aus {class_url}")
        except Exception as e:
            logging.error(f"Fehler beim Klicken auf den 'Änderungen speichern'-Button: {e}")
            continue

        # Optional: Warten, damit die Änderungen serverseitig verarbeitet werden
        time.sleep(1)
    
    return processed_course_ids

def extract_course_ids(driver, waittime):
    CourseIDs = set()  # Verwende ein Set für eindeutige Kurs-IDs
    courses_url = 'https://lernplattform.mebis.bycs.de/my/courses.php'
    print("Navigiere zur Kursseite...")
    driver.get(courses_url)

    # Alle Links zu Kursen finden
    WebDriverWait(driver, waittime).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='course/view.php?id=']")))
    course_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='course/view.php?id=']")
    print(f"Gefundene Kurslinks: {len(course_links)}")
    for link in course_links:
        CourseID = re.search(r'id=(\d+)', link.get_attribute("href")).group(1)
        CourseIDs.add(CourseID)  # Füge zur Menge hinzu
    
    print(f"Extrahierte Kurs-IDs: {list(CourseIDs)}")  # Konvertiere zurück zu Liste für die Ausgabe
    return list(CourseIDs)  # Gib die Kurs-IDs als Liste zurück


def main():
    config = load_config()
    
    username = config['login']['username']
    password = config['login']['password']
    waittime = int(config['mode']['waittime'].strip())
    
    headless = config['mode']['headless'].strip().lower() == "true"
    csv_file_path = 'processed_course_ids.csv'
    
    # Bereits verarbeitete Kurs-IDs einlesen
    processed_course_ids = read_course_ids_from_csv(csv_file_path)
    
    # Vordefinierte Kurs-IDs aus der Konfiguration lesen und von bereits
    # verarbeiteten Kurs-IDs subtrahieren.
    predefined_course_ids = set()
    if 'course_ids' in config['courses']:
        predefined_course_ids = {cid.strip() for cid in config['courses']['course_ids'].split(',')}
    
    # Neue Kurs-IDs bestimmen: Nur solche, die noch nicht verarbeitet wurden
    if predefined_course_ids:
        course_ids_to_process = predefined_course_ids - processed_course_ids
        logging.info(f"Vordefinierte Kurs-IDs (nach Filterung): {course_ids_to_process}")
    else:
        course_ids = extract_course_ids(driver, waittime)
        course_ids_to_process = {cid for cid in course_ids if cid not in processed_course_ids}
        logging.info(f"Kurs-IDs, die jetzt verarbeitet werden: {course_ids_to_process}")
    
    driver = create_webdriver(headless=headless)    
    try:
        login(driver, username, password, waittime)
        
        # Klassenlinks aller zu verarbeitenden Kurse abrufen
        all_classes = []
        for course_id in course_ids_to_process:
            classes = extract_classes(driver, course_id, waittime)
            all_classes.extend(classes)
        
        # Klassen verarbeiten und erfolgreiche Kurs-IDs zurückgeben
        successfully_processed_ids = process_classes(driver, all_classes, waittime)
        
        # Speichern, falls neue IDs erfolgreich bearbeitet wurden
        if successfully_processed_ids:
            write_course_ids_to_csv(csv_file_path, successfully_processed_ids)
            logging.info("Alle Änderungen wurden erfolgreich gespeichert.")
        else:
            logging.info("Keine Änderungen wurden vorgenommen.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()