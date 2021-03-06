from flask import Flask, render_template, request, flash

from pprint import pformat, pprint
import os
import requests
from random import choice


app = Flask(__name__)
app.secret_key = 'SECRETSECRETSECRET'

# This configuration option makes the Flask interactive debugger
# more useful (you should remove this line in production though)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True


API_KEY = os.environ['TICKETMASTER_KEY']


@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')


@app.route('/afterparty')
def show_afterparty_form():
    """Show event search form"""

    return render_template('search-form.html')


@app.route('/afterparty/search')
def find_afterparties():
    """Search for afterparties on Ticketmaster"""

    keyword = request.args.get('keyword', '')
    postalcode = request.args.get('zipcode', '')
    radius = request.args.get('radius', '')
    unit = request.args.get('unit', '')
    sort = request.args.get('sort', '')

    url = 'https://app.ticketmaster.com/discovery/v2/events'
    payload = {'apikey': API_KEY}

    #
    # - Use form data from the user to populate any search parameters
    #
    # - Make sure to save the JSON data from the response to the `data`
    #   variable so that it can display on the page. This is useful for
    #   debugging purposes!
    #
    # - Replace the empty list in `events` with the list of events from your
    #   search results
    
    payload['keyword'] = keyword
    payload['postalCode'] = postalcode
    payload['radius'] = radius
    payload['unit'] = unit
    payload['sort'] = sort

    res = requests.get(url, params=payload)
    data = res.json()
    pprint(data)
    if '_embedded' in data:
        events = data['_embedded']['events']
        return render_template('search-results.html',
                               pformat=pformat,
                               data=data,
                               results=events)
    else:
        flash("Oops, none found! Try again")
        return render_template('search-form.html')



# ===========================================================================
# FURTHER STUDY
# ===========================================================================


@app.route('/event/<id>')
def get_event_details(id):
    """View the details of an event."""

    url = f'https://app.ticketmaster.com/discovery/v2/events/{id}'
    payload = {'apikey': API_KEY}
    res = requests.get(url, params=payload)
    data = res.json()
    pprint(data)
    
    event_name = data['name']
    
    event_description = data.get('info', "No description found.")
    start = data['dates']['start'].get('localDate', "")
    tickets = data['url']

    pictures = []
    for each_dict in data['images']:
        pictures.append(each_dict['url'])
    picture = choice(pictures)

    classifications = data['classifications']
    class_ = []
    if classifications:
        for ii in range(len(classifications)):
            class_.append(classifications[ii]['genre']['name'])

    venues = data['_embedded']['venues']
    venues_ = []
    if venues:
        for jj in range(len(venues)):
            venues_.append(venues[jj]['name'])


    return render_template('event-details.html', NAME=event_name, DESCRIPTION=event_description, PICS=picture, TIX=tickets, START=start, VENUES=venues_, CLASS=class_)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
