from flask import Flask,render_template,request
from dataset import mobile_data
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

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

def suggestPhone(ram, storage, camera, lower_price_range, upper_price_range, battery, mobile_phones):
    
    try:
        phones_in_price_range = [
            phone for phone in mobile_phones
            if lower_price_range <= int(phone[7].replace('₹', '').replace(',', '')) <= upper_price_range
        ]

        aval_ram = [float(phone[3].replace("GB", "")) for phone in phones_in_price_range]
        aval_camera = [float(phone[5].split("MP")[0].strip()) for phone in phones_in_price_range]
        aval_storage = [float(phone[2].replace("GB", "")) for phone in phones_in_price_range]
        aval_battery = [int(phone[6]) for phone in phones_in_price_range]

        closest_match_ram = find_closest(ram, aval_ram)
        closest_match_camera = find_closest(camera, aval_camera) 
        closest_match_storage = find_closest(storage, aval_storage)
        closest_match_battery = find_closest(battery, aval_battery)

        for phone in phones_in_price_range:
            phone_ram = float(phone[3].replace("GB", "").strip())
            phone_camera = float(phone[5].split("MP")[0].strip()) 
            phone_storage = float(phone[2].replace("GB", "").strip())
            phone_battery = int(phone[6].replace("mAh", "").strip())

            if (phone_ram in closest_match_ram and
                phone_camera in closest_match_camera and
                phone_storage in closest_match_storage and phone_battery in closest_match_battery):

                return phone
    
    except Exception as e:
        print("Error occured while rendering Suggestions \n", e)

    return "No"

def recommendPhone(ram, rom, camera, price, battery):
    
    try:
        df = pd.read_csv("phones_data.csv")
        features = df[['Battery Capacity (mAh)', 'Primary Camera (MP)', 'Price (Rs)', 'RAM (GB)', 'Storage (GB)']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        knn = NearestNeighbors(n_neighbors=6) 
        knn.fit(scaled_features)

        input_data = [[battery, camera, price, ram, rom]]
        scaled_input = scaler.transform(input_data)

        distances, indices = knn.kneighbors(scaled_input)
        recommended_phones = df.iloc[indices[0]].to_dict(orient='records')

        return recommended_phones
    
    except Exception as e:
        print("Error occured while rendering Recommendations \n", e)

@app.route('/',methods = ['GET','POST'])
def home():
    
    if request.method == 'POST':
        try:
            ram = float(request.form['ram'])
            storage = float(request.form['storage'])
            camera = float(request.form['camera'])
            battery = int(request.form['battery'].lower().replace('mah', "").strip())
            lower_price_range = int(request.form['lower_price_range'])
            higher_price_range = int(request.form['higher_price_range'])
            
            recommended_phones = recommendPhone(ram, storage, camera, (lower_price_range+higher_price_range)//2, battery)
            suggested_phone = suggestPhone(ram, storage, camera, lower_price_range, higher_price_range,battery, mobile_data)
            
            return render_template('home.html', suggestion=suggested_phone, recommendation=recommended_phones)
        
        except Exception as e:
            print("Error occured while filling up the form \n", e)
    
    return render_template('home.html', suggestion=None, recommendation=None)
        
if __name__ =='__main__':
    app.run(debug=True)
