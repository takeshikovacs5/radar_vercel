from flask import Flask, render_template, request, jsonify, redirect, url_for, json
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField
import pandas as pd
from soccerplots.radar_chart import Radar
import matplotlib
import matplotlib.pyplot as plt, mpld3
matplotlib.use('Agg')
from io import BytesIO
import base64
from PIL import Image
import requests
from mplsoccer import add_image
from urllib.request import urlopen
import matplotlib.font_manager as fm

fpath = "fonts/Poppins/Poppins-Regular.ttf"
prop = fm.FontProperties(fname=fpath)

fpath_bold = "fonts/Poppins/Poppins-SemiBold.ttf"
prop_bold = fm.FontProperties(fname=fpath_bold)

fpath_bold2 = "fonts/Poppins/Poppins-Bold.ttf"
prop_bold2 = fm.FontProperties(fname=fpath_bold2)

font_dirs = ["fonts/Poppins/Poppins.ttf"]  # The path to the custom font file.
font_files = fm.findSystemFonts(fontpaths=font_dirs)

for font_file in font_files:
    fm.fontManager.addfont(font_file)

app = Flask(__name__)
app.secret_key = "FotMob_Radar"

# Form for player selection
class PlayerSelectForm(FlaskForm):
    player1_name = SelectField('Select Player 1')
    player2_name = SelectField('Select Player 2')

@app.route("/", methods=["GET", "POST"])
def index():
    selectedposition = request.form.get('position', 'FW')
    if selectedposition == 'FW':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/forwards.csv'
    elif selectedposition == 'MF':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/midfielders.csv'
    elif selectedposition == 'DF':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/defenders.csv'
    else:
    # Handle the case when an invalid position is selected
        print(f"Invalid position: {selectedposition}")
    # You might want to provide a default CSV or terminate the script
    df = pd.read_csv(csv_url)

    # Create a list of unique player names from the 'player.name' column
    unique_players = sorted(df['player.name'].unique())

    # Provide choices to the form fields
    form = PlayerSelectForm()

    # Set choices when rendering the page
    form.player1_name.choices = [(player, player) for player in unique_players]
    form.player2_name.choices = [(player, player) for player in unique_players]

    if form.validate_on_submit():
        selected_player1 = form.player1_name.data
        selected_player2 = form.player2_name.data

        # Redirect to the radar_chart route with the selected players
        return redirect(url_for('radar_chart', player1_name=selected_player1, player2_name=selected_player2))

    return render_template('index.html', form=form)


@app.route("/radar_chart", methods=["GET", "POST"])
def radar_chart():
    form = PlayerSelectForm(request.form)  # Use the form with submitted data
    selectedposition = request.form.get('selected_position')

    player1 = request.form.get('player1_name')
    player2 = request.form.get('player2_name')

    print(f"Received data: Player 1 - {player1}, Player 2 - {player2}")

    if not player1 or not player2:
        return jsonify({'error': 'Invalid player names'})
    
    if selectedposition == 'FW':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/forwards.csv'
    elif selectedposition == 'MF':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/midfielders.csv'
    elif selectedposition == 'DF':
        csv_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/defenders.csv'
    df = pd.read_csv(csv_url)

    # get parameters
    params = list(df.columns)
    params = params[:-4]

    # add ranges to list of tuple pairs
    ranges = []
    a_values = []
    b_values = []

    for x in params:
        a = min(df[params][x])

        b = max(df[params][x])

        ranges.append((a, b))

    df_filtered = df[(df['player.name'] == player1) | (df['player.name'] == player2)].reset_index()
    player1_row = df_filtered[(df_filtered['player.name'] == player1)].reset_index()
    player2_row = df_filtered[(df_filtered['player.name'] == player2)].reset_index()

    if ((selectedposition == 'MF') | (selectedposition == 'DF')):
        team1name = player1_row['team.name']
        team1shortname = player1_row['team.shortName']
        if team1name.isnull().values.any() == True:
            takim1 = team1shortname.iloc[0]
        elif team1shortname.isnull().values.any() == True:
            takim1 = team1name.iloc[0]

        team2name = player2_row['team.name']
        team2shortname = player2_row['team.shortName']
        if team2name.isnull().values.any() == True:
            takim2 = team2shortname.iloc[0]
        elif team2shortname.isnull().values.any() == True:
            takim2 = team2name.iloc[0]
        
    elif selectedposition == 'FW':
        team1name = player1_row['team.name']
        takim1 = team1name.iloc[0]
        team2name = player2_row['team.name']
        takim2 = team2name.iloc[0]

    ligsezon = 'Süper Lig | 23/24'
    endnote = '90 dakika başına düşen verilerdir'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

    fotmob_df_url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/fotmob_id.csv'
    fotmob_df = pd.read_csv(fotmob_df_url)
    player1_fotmob = fotmob_df.loc[fotmob_df['player_name'] == player1, 'fotmob_id'].values
    player1_fotmob_id = player1_fotmob[0]
    player2_fotmob = fotmob_df.loc[fotmob_df['player_name'] == player2, 'fotmob_id'].values
    player2_fotmob_id = player2_fotmob[0]
    player1_fotmob_photo_url = 'https://images.fotmob.com/image_resources/playerimages/'+str(player1_fotmob_id)+'.png'
    player2_fotmob_photo_url = 'https://images.fotmob.com/image_resources/playerimages/'+str(player2_fotmob_id)+'.png'
    r_player1 = urlopen(player1_fotmob_photo_url)
    r_player2 = urlopen(player2_fotmob_photo_url)
    player1_foto = Image.open(r_player1)
    player2_foto = Image.open(r_player2)
    
    df_filtered = df_filtered.drop(['index', 'team.name', 'team.shortName'], axis=1)

    for x in range(len(df_filtered['player.name'])):
        if df_filtered['player.name'][x] == player1:
            a_values = df_filtered.iloc[x].values.tolist()
        if df_filtered['player.name'][x] == player2:
            b_values = df_filtered.iloc[x].values.tolist()

    values = [a_values, b_values]

    radar_renk1 = '#3498db'  # Blue
    radar_renk2 = '#e67e22'  # Orange

    title = dict(
        title_name=f"{player1}\n",
        title_color=radar_renk1,  # Set your color for player1
        subtitle_name=f"{takim1}\n{ligsezon}",
        subtitle_color=radar_renk1,
        title_name_2=f"{player2}\n",
        title_color_2=radar_renk2,  # Set your color for player2
        subtitle_name_2=f"{takim2}\n{ligsezon}",
        subtitle_color_2=radar_renk2
    )

    radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF",
                    range_color="#FFFFFF", label_fontsize=9.5, range_fontsize=8.5,
                    fontfamily='Poppins')
    
    
    if selectedposition == 'FW':
        fig, ax = radar.plot_radar(ranges=ranges, params=['Gol', 'Gol Beklentisi (xG)', 'Toplam Şut', 'İsabetli Şut', 'Pozisyonu Gole\nÇevirme %',
    'Başarılı Top\nSürme', 'Başarılı Top\nSürme %', 'Yaratılan Büyük\nŞans', 'Kilit Pas',
    'Rakip Gol Bölgesinde\nİsabetli Pas', 'Zeminde Kazanılan\nİkili Mücadele', 'Kazanılan Hava\nTopu Mücadelesi', 'Kazanılan Toplam\nİkili Mücadele %', 'Kendisine Yapılan\nFaul'],
                                    values=values,
                                    radar_color=[radar_renk1, radar_renk2],
                                    alphas=[0.65, 0.6], title=title, endnote=endnote,
                                    compare=True)
    if selectedposition == 'MF':
        fig, ax = radar.plot_radar(ranges=ranges, params=['Gol', 'Başarılı Top\nSürme', 'Başarılı Top\nSürme %', 'Toplam Şut', 'İsabetli Şut',
    'Yaratılan Büyük\nŞans', 'İsabetli Pas', 'İsabetli Pas %', 'Kilit Pas', 'İsabetli Orta',
    'İsabetli Uzun Top', 'Top Çalma', 'Pas Arası', 'Zeminde Kazanılan\nİkili Mücadele', 'Kazanılan Hava\nTopu Mücadelesi',
    'Kazanılan Toplam\nİkili Mücadele %', 'Kendisine Yapılan\nFaul'],
                                    values=values,
                                    radar_color=[radar_renk1, radar_renk2],
                                    alphas=[0.65, 0.6], title=title, endnote=endnote,
                                    compare=True)
    if selectedposition == 'DF':
        fig, ax = radar.plot_radar(ranges=ranges, params=['Top Çalma', 'Pas Arası', 'Top Uzaklaştırma', 'İsabetli Pas', 'İsabetli Pas %',
    'İsabetli Orta', 'İsabetli Orta %', 'İsabetli Uzun Top', 'İsabetli Uzun Top %',
    'Başarılı Top\nSürme', 'Zeminde Kazanılan\nİkili Mücadele', 'Kazanılan Hava\nTopu Mücadelesi', 'Kazanılan Toplam\nİkili Mücadele', 'Kazanılan Toplam\nİkili Mücadele %'],
                                    values=values,
                                    radar_color=[radar_renk1, radar_renk2],
                                    alphas=[0.65, 0.6], title=title, endnote=endnote,
                                    compare=True)
        
    ax_image_1 = add_image(player1_foto, fig=fig, left=0.310, bottom=0.940, width=0.1, height=0.1, interpolation='hanning')
    ax_image_2 = add_image(player2_foto, fig=fig, left=0.614, bottom=0.940, width=0.1, height=0.1, interpolation='hanning')

    # Save the figure as a BytesIO object
    img_stream = BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', pad_inches=0.1,
          facecolor='auto', edgecolor='auto')
    img_stream.seek(0)

    # Convert the BytesIO object to base64 for embedding in HTML
    img_str = 'data:image/png;base64,' + base64.b64encode(img_stream.read()).decode('utf-8')

    plt.close()  # Close the Matplotlib plot to avoid resource leaks

    return render_template("radar_chart.html", form=form, chart_img=img_str)

if __name__ == '__main__':
    app.run(debug=True)
