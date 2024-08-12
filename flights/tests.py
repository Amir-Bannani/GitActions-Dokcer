from django.test import TestCase, Client

from .models import Flight, Passenger, Airport

from django.db.models import Max

# Import Max : an aggregation function

class FlightTestCase(TestCase):
    # The functio to run when execution (defines the Test dataBase)
    # Create entries for the dataBase
    def setUp(self):
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a1, destination=a1, duration=100)
        Flight.objects.create(origin=a1, destination=a2, duration=-100)

    def test_departures_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertTrue(a.departures.count(), 3)

    def test_arrivals_count(self):
        b = Airport.objects.get(code="BBB")
        self.assertTrue(b.arrivals.count(), 2)

    def test_valid_flight(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        flight = Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertFalse(flight.is_valid())

    def test_invalid_flight_destination(self):
        a1 = Airport.objects.get(code="AAA")
        flight = Flight.objects.get(origin=a1, destination=a1, duration=100)
        self.assertFalse(flight.is_valid())

    def test_invalid_flight_duration(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        flight = Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(flight.is_valid())


    def test_index(self):
        # Set up a client  to make request

        c = Client()

        # Send get response to index page and store response

        reponse = c.get("/flights/")

        # Make sure the status_code is 200
        self.assertEqual(reponse.status_code, 200)

        # Mkae sure three flights returned in the context
        self.assertEqual(reponse.context["flights"].count(), 3)


    def test_flight_exists(self):
        c = Client()
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_flight_not_exists(self):
        c = Client()
        
        # Get the maximum id available in the flights Objects

        max_id = Flight.objects.all().aggregate(max_id= Max("id"))["max_id"]

        # Try to get a flight Page that does not exist

        response = c.get(f"/flights/{max_id+1}")

        self.assertEqual(response.status_code, 404)


    def test_passenger_exist(self):
        c = Client()
        p = Passenger.objects.create(first="amir", last="ka")
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)
        f.passengers.add(p)
        response = c.get(f"/flights/{f.id}") 

        self.assertEqual(response.context["passengers"].count(), 1)

    
    def test_non_passenger_exist(self):
        c = Client()
        p = Passenger.objects.create(first="astro", last="adaf")
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)

        response = c.get(f"/flights/{f.id}") 


        self.assertEqual(response.context["non_passengers"].count(), 1)
        
        


    




