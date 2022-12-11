import json
import overpy
from rest_framework import generics, permissions, status
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from . import serializers
from .models import Profile
from .serializers import UserSerializer, RegisterSerializer, UpdateLocationSerializer, OverpassSerializer
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.gis.geos import Point, Polygon


# Register APIView - serializes data from request and creates user it if all checks out
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# LoginView - takes username and password. Serializes it and tries to authenticate the user
# returns error if credentials are invalid
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request,  format=None)


# function to update the database - gets profile object by request.
# passes user into serializer with data and updates the location
@api_view(['POST'])
def update_database(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        data = request.data
        serializer = UpdateLocationSerializer(instance=profile, data=data)
        if serializer.is_valid():
            my_location = request.data['last_location']
            my_coords = [float(coord) for coord in my_location.split(", ")]
            profile.last_location = Point(my_coords)
            profile.save()
            serializer.save()

            return Response(data=data)
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# tries to get the user object of a user - if success user is authenticated otherwise they aren't
@api_view(['POST'])
def check_authentication(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        data = request.data

        return Response(data=data)
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QueryOverpass(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = serializers.OverpassSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Create overpass API object
            api = overpy.Overpass()

            # creating placeholder for the top and bottom of the query.
            api_query_top = \
                """
                [out:json][timeout:25];
                (
                """

            api_query_bottom = \
                """
                );
                out body;
                >;
                out skel qt;
                """

            api_middle = ""

            # Run our incoming data through the serializer to validate and pre-process it.
            my_serializer = serializers.OverpassSerializer(data=request.data)
            if my_serializer.is_valid():
                bbox = my_serializer.validated_data["bbox"]
                for item in my_serializer.validated_data["query"]:
                    if item == "*":
                        api_middle += f'node["amenity"]{tuple(bbox)};\nway["amenity"]{tuple(bbox)};\nrelation["amenity"]{tuple(bbox)};'
                        break
                    else:
                        api_middle += f'node["amenity"="{item}"]{tuple(bbox)};\nway["amenity"="{item}"]{tuple(bbox)};\nrelation["amenity"="{item}"]{tuple(bbox)};'

                api_query = f"{api_query_top}\n{api_middle}\n{api_query_bottom}\n"
                result = api.query(api_query)

                # The result should be returned as GeoJSON. A Python dictionary with a list of 'features' can be easily
                # serialized as GeoJSON
                geojson_result = {
                    "type": "FeatureCollection",
                    "features": [],
                }

                # This next section iterates through each 'way' and gets its centroid. It also keeps a record of the
                # points in the so that they are not duplicated when we process the 'nodes'
                nodes_in_way = []

                for way in result.ways:
                    geojson_feature = None
                    geojson_feature = {
                        "type": "Feature",
                        "id": "",
                        "geometry": "",
                        "properties": {}
                    }
                    poly = []
                    for node in way.nodes:
                        # gets nodes and makes a polygon
                        nodes_in_way.append(node.id)
                        poly.append([float(node.lon), float(node.lat)])
                    # Make a poly out of the nodes in way.
                    # Some ways are badly made so, if we can't succeed just ignore the way and move on.
                    try:
                        poly = Polygon(poly)
                    except:
                        continue
                    geojson_feature["id"] = f"way_{way.id}"
                    geojson_feature["geometry"] = json.loads(poly.centroid.geojson)
                    geojson_feature["properties"] = {}
                    for k, v in way.tags.items():
                        geojson_feature["properties"][k] = v

                    geojson_result["features"].append(geojson_feature)

                # gets the results that are nodes
                for node in result.nodes:
                    # ignore the nodes that are in a way so they're not gotten twice
                    if node.id in nodes_in_way:
                        continue
                    geojson_feature = None
                    geojson_feature = {
                        "type": "Feature",
                        "id": "",
                        "geometry": "",
                        "properties": {}
                    }
                    point = Point([float(node.lon), float(node.lat)])
                    geojson_feature["id"] = f"node_{node.id}"
                    geojson_feature["geometry"] = json.loads(point.geojson)
                    geojson_feature["properties"] = {}
                    for k, v in node.tags.items():
                        geojson_feature["properties"][k] = v

                    geojson_result["features"].append(geojson_feature)

                # Return in GeoJSON structure.
                return Response(geojson_result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Error: {e}."}, status=status.HTTP_400_BAD_REQUEST)














