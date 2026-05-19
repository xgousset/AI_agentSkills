import requests
import xml.etree.ElementTree as ET

def poll_feeds():
    """
    Polls a list of official emergency RSS feeds (simulated for readiness).
    """
    feeds = [
        "https://www.interieur.gouv.fr/rss/actu.xml",
        "https://www.vigicrues.gouv.fr/rss/",
        # "http://meteofrance.com/rss/previsions" # Example
    ]
    
    alerts = []
    for feed in feeds:
        try:
            response = requests.get(feed, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item')[:3]:
                    alerts.append({
                        "title": item.find('title').text,
                        "link": item.find('link').text,
                        "source": feed
                    })
        except:
            continue
            
    return alerts

if __name__ == "__main__":
    print(poll_feeds())
