import sqlite3
import analyzer as a
import dataRAW
import valo_api as val
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from matplotlib import image 
from matplotlib import pyplot as plt

# https://dash.valorant-api.com/endpoints/maps
def calc_percent():
    pass

# gets the raw kill coordinates given a game object 
# DEPRECATED
def get_raw_kill_coords(game):
    all_kills = []

    for round in game.rounds:
        for player in round.player_stats:
            for kill_event in player.kill_events:
                # death locations (comment out for kills)
                victim_death_location = [kill_event.victim_death_location.x, kill_event.victim_death_location.y]
                all_kills.append(victim_death_location)

                # kill locations
                # for player in kill_event.player_locations_on_kill:
                #     all_kills.append([player.location.x, player.location.y])

        # all_kills.append(round_eventfeed)2

    return all_kills

def get_kills(match_id):
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    # grab actor_x
    query = """SELECT actor_x, actor_y FROM RoundEvents WHERE match_id = ? AND action = ?"""
    cursor.execute(query, (match_id, "Kill"))
    kills = [list(i) for i in cursor.fetchall()]

    return kills

def get_deaths(match_id):
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    # grab actor_x
    query = """SELECT victim_death_x, victim_death_y FROM RoundEvents WHERE match_id = ? AND action = ?"""
    cursor.execute(query, (match_id, "Kill"))
    deaths = [list(i) for i in cursor.fetchall()]

    return deaths

def get_plants(match_id):
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    # grab actor_x
    query = """SELECT actor_x, actor_y FROM RoundEvents WHERE match_id = ? AND action = ?"""
    cursor.execute(query, (match_id, "Plant"))
    plants = [list(i) for i in cursor.fetchall()]

    return plants

# process the kill coordinates into image coordinates
# events_loc looks like [[x1, y1], [x2, y2], etc.]
def process_hmap_coords(events_loc, uuid):
    resp = requests.get("https://valorant-api.com/v1/maps/" + uuid)
    data = resp.json()
    img_resp = requests.get("https://media.valorant-api.com/maps/" + uuid + "/displayicon.png")
    img = Image.open(BytesIO(img_resp.content))

    map_x_multiplier = float(data["data"]["xMultiplier"])
    map_y_multiplier = float(data["data"]["yMultiplier"])
    map_x_scalar = data["data"]["xScalarToAdd"]
    map_y_scalar = data["data"]["yScalarToAdd"]

    map_death_coords = []
    
    for game_xy in events_loc:
        game_x = game_xy[0]
        game_y = game_xy[1]
        map_x = game_y * map_x_multiplier + map_x_scalar
        map_y = game_x * map_y_multiplier + map_y_scalar
        map_x *= img.width
        map_y = (1 - map_y) * img.height

        # map_y = img.width - map_y
        map_death_coords.append([map_x, map_y])
    return [img, map_death_coords]

def gaussian_filter(arr, sigma):
    """Apply Gaussian filter to array for smoothing."""
    filter_size = int(6 * sigma + 0.5)
    gaussian_filter = np.exp(-np.linspace(-(filter_size // 2), filter_size // 2, filter_size)**2 / (2 * sigma**2))
    gaussian_filter /= gaussian_filter.sum()
    arr = np.apply_along_axis(lambda m: np.convolve(m, gaussian_filter, mode='same'), axis=0, arr=arr)
    arr = np.apply_along_axis(lambda m: np.convolve(m, gaussian_filter, mode='same'), axis=1, arr=arr)
    return arr

# lower bins for representative of groupings
def plot_coords(coords, im, smoothing_sigma=14.5, bins=800):
    img = np.array(im)
    
    # Extract x and y coordinates
    coord_x = [point[0] for point in coords]
    coord_y = [point[1] for point in coords]
    
    # Define the bins for the heatmap
    x_bins = np.linspace(0, img.shape[1], bins)
    y_bins = np.linspace(0, img.shape[0], bins)
    
    # Create a histogram2d for the x and y coordinates
    heatmap, xedges, yedges = np.histogram2d(coord_x, coord_y, bins=[x_bins, y_bins])
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    # Apply a gaussian filter to smooth the heatmap
    heatmap_smoothed = gaussian_filter(heatmap.T, sigma=smoothing_sigma)
    
    # Plot the image
    plt.imshow(img, extent=extent, aspect='auto')
    
    # Overlay the smoothed heatmap
    plt.imshow(heatmap_smoothed, extent=extent, origin='lower', cmap='magma', alpha=0.5)
    
    # Add a colorbar with a label
    plt.colorbar(label='Density')
    plt.savefig("img/hmap.png")

def main():
    # for games not in db
    # history = a.get_recent_matches("na", "Cytosine", "7670", size=1, game_mode="competitive", map="Bind")
    game = "d9a35d2a-1619-4109-8fc2-8344c8a94bc5"
    deaths = get_deaths(game)
    plants = get_plants(game)
    uuid = dataRAW.get_map(game)[1]
    processed = process_hmap_coords(plants, uuid)

    img = processed[0]
    events = processed[1]

    plot_coords(events, img)

if __name__ == "__main__":
    main()