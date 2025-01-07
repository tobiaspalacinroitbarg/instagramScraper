from funcs import login, get_reels
import time

USERNAME = "ParkourIns4n3aa"
PASSWORD = "asd1234MM"

driver = login(USERNAME, PASSWORD)

results = get_reels(driver)

print(results)