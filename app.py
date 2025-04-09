from flask import Flask,render_template,request
from dataset import mobile_data
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Find the closest match value
def find_closest(value, options):
    min_diff = abs(value - options[0])
    for x in range(1, len(options)):
        temp = abs(value - options[x])
        if min_diff > temp:
            min_diff = temp

    closest_match = []
    for x in options:
        if min_diff == abs(value - x):
            closest_match.append(x)

    return closest_match

# Function to suggest a phone based on the nearest specifications
def choice_phone(ram, storage, camera, lower_price_range, upper_price_range, battery, mobile_phones):

    # Filter phones by price range
    phones_in_price_range = [
        phone for phone in mobile_phones
        if lower_price_range <= int(phone[7].replace('₹', '').replace(',', '')) <= upper_price_range
    ]

    # Extract the specifications from the filtered phones
    aval_ram = [float(phone[3].replace("GB", "")) for phone in phones_in_price_range]
    aval_camera = [float(phone[5].split("MP")[0].strip()) for phone in phones_in_price_range]  # Use only the first camera spec
    aval_storage = [float(phone[2].replace("GB", "")) for phone in phones_in_price_range]
    aval_battery = [int(phone[6]) for phone in phones_in_price_range]

    # Get the closest values for each specification
    closest_match_ram = find_closest(ram, aval_ram)
    closest_match_camera = find_closest(camera, aval_camera)  # Use only the first camera value
    closest_match_storage = find_closest(storage, aval_storage)
    closest_match_battery = find_closest(battery, aval_battery)

    print(aval_battery)
    print(closest_match_battery)
    # Find and return the matching phone based on the closest specs
    for phone in phones_in_price_range:
        phone_ram = float(phone[3].replace("GB", "").strip())
        phone_camera = float(phone[5].split("MP")[0].strip())  # Consider only the first camera value
        phone_storage = float(phone[2].replace("GB", "").strip())
        phone_battery = int(phone[6].replace("mAh", "").strip())

        if (phone_ram in closest_match_ram and
            phone_camera in closest_match_camera and
            phone_storage in closest_match_storage and phone_battery in closest_match_battery):

            print("Match found")
            return phone

    return None

def recommendPhone(ram, rom, camera, price, battery):

    df = pd.read_csv("phones_data.csv")
    features = df[['Battery Capacity (mAh)', 'Primary Camera (MP)', 'Price (Rs)', 'RAM (GB)', 'Storage (GB)']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    knn = NearestNeighbors(n_neighbors=5) 
    knn.fit(scaled_features)

    input_data = [[battery, camera, price, ram, rom]]
    scaled_input = scaler.transform(input_data)

    distances, indices = knn.kneighbors(scaled_input)
    recommended_phones = df.iloc[indices[0]].to_dict(orient='records')

    return recommended_phones

@app.route('/',methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        ram = float(request.form['ram'])
        storage = float(request.form['storage'])
        camera = float(request.form['camera'])
        battery = int(request.form['battery'])
        lower_price_range = int(request.form['lower_price_range'])
        higher_price_range = int(request.form['higher_price_range'])
        recommended_phones = recommendPhone(ram, storage, camera, (lower_price_range+higher_price_range)//2, battery)
        suggested_phone = choice_phone(ram, storage, camera, lower_price_range, higher_price_range,battery, mobile_data)
        return render_template('home.html', suggestion=suggested_phone, recommendation=recommended_phones)

    return render_template('home.html', suggestion=None, recommendation=None)
        
if __name__ =='__main__':
    app.run(debug=True)
