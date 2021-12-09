from app import app
from flask import render_template, request
from app.models.company import Company

@app.route('/')
def index():
    return render_template('index.html')

companies = [Company.make("WLKP"), Company.make("MSFT"), Company.make("CMC")]
@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
    if request.method == "POST":
        companies.append(Company.make(request.form.to_dict().get('symbol')))
        return Company.repr_card_grid(companies)

    card_grid = Company.repr_card_grid(companies)
    return render_template('dashboard.html', card_grid=card_grid)


if __name__ == '__main__':
   app.run()
