from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Trains(db.Model):
    __tablename__ = "Trains"
    train_no = db.Column(db.Integer,primary_key=True)
    depart = db.Column(db.String(60))
    arrival = db.Column(db.String(60))
    fare = db.Column(db.Integer,nullable = False)


class Destination(db.Model):
    __tablename__ = "Destination"
    destination_name = db.Column(db.String(120),primary_key=True)
    dest_city = db.Column(db.String(120),nullable = False)
    train_no_to = db.Column(db.String(20),db.ForeignKey('Trains.train_no'),nullable = True)
    train_no_from = db.Column(db.String(20,db.ForeignKey('Trains.train_no')),nullable = True)
    train = db.relationship('Trains', backref='destination', lazy=True)


def get_vals_destination(dest_name):
    with app.app_context():
        entries = Destination.query.all()

        for entry in entries:
            print(f"Checking: {entry.destination_name}")
            if entry.destination_name == dest_name:
                return [entry.destination_name, entry.dest_city, entry.train_no_to, entry.train_no_from]

    return []
def get_fares_and_times(t1):
    train = Trains.query.filter_by(train_no=t1).first()
    return train.fare , train.depart

def get_plans(option,budget):
        with app.app_context():
            data = get_vals_destination(option)
            print(data)
            if data[0] =="Sri Venkateshwara Temple":
                data.extend([60,60,0,0])
            elif data[2] == None and data[0] != "Sri Venkateshwara Temple":
                data.extend([30,30,0,0])
            else:
                fare1 , depart_time1 = get_fares_and_times(data[2])
                fare2 , depart_time2 = get_fares_and_times(data[3])
                data.extend([fare1,fare2,depart_time1,depart_time2])
            print(data)
            total_fare_cost = data[4] + data[5]
            return data , total_fare_cost

user_selections ={}


#First page to be loaded

@app.route('/')
def categories():
    return render_template('index.html')

@app.route('/option/<category>')
def options(category):
    user_selections['category'] = category
    return render_template('option.html', category=category)

@app.route('/budget/<category>/<option>')
def budget(category, option):
    user_selections['category'] = category
    user_selections['option'] = option
    return render_template('budget.html')

@app.route('/results', methods=['POST'])
def results():
    budget = request.form.get('budget')
    option = user_selections.get('option')
    plans, min_value =  get_plans(option,budget)

    return render_template('results.html',train_no_to=plans[2],dest_city =plans[1],dest_name = plans[0],train_no_from=plans[3],
                            start_fare = plans[4],end_fare = plans[5],start_time = plans[6],end_time = plans[7],
                            travel_cost = min_value,balance_amount = int(budget)-min_value)
    

if __name__ == '__main__':
    

    # Run the Flask app
    app.run(debug=True)