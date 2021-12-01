from flask import Flask, render_template, request, flash

from pprint import pformat
import os
import requests
from pprint import pprint
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
    payload = {'apikey': os.environ['TICKETMASTER_KEY']}

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

    url = 'https://app.ticketmaster.com/discovery/v2/events'
    payload = {'apikey': os.environ['TICKETMASTER_KEY'], 'id': id}

    res = requests.get(url, params=payload)
    data = res.json()
    pprint(data)
    
    
    event_name = data['_embedded']['events'][0]['name']
    if 'description' in data['_embedded']['events'][0]:
        event_description = data['_embedded']['events'][0]['description']
    else:
        event_description = ""

    venues = ['1', '2', '3']
    #picture = data['_embedded']['events'][0]['images'][0]['url']    
    pictures = []
    for each_dict in data['_embedded']['events'][0]['images']:
        pictures.append(each_dict['url'])
    picture = choice(pictures)
    tickets = data['_embedded']['events'][0]['url']
    if 'dateTime' in data['_embedded']['events'][0]['dates']['start']:
        start = data['_embedded']['events'][0]['dates']['start']['dateTime']
    else:
        start = ""
    
    class_ = data['_embedded']['events'][0]['classifications']

    return render_template('event-details.html', NAME=event_name, DESCRIPTION=event_description, VENUES=venues, CLASS=class_, PICS=picture, TIX=tickets, START=start)
    #else:
    #        flash("Not a good record. Please try again.")
    #        return render_template('search-form.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
