import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { LocationProvider } from './src/context/LocationContext';
import { HomeScreen } from './src/screens/HomeScreen';
import { AddRouteScreen } from './src/screens/AddRouteScreen';

type RootStackParamList = {
  Home: { firebaseUid: string };
  AddRoute: { firebaseUid: string };
};

const Stack = createStackNavigator<RootStackParamList>();

// Mock Firebase UID for development
// In production, this would come from Firebase Authentication
const DEVELOPMENT_FIREBASE_UID = 'dev-user-123';

export default function App() {
  return (
    <LocationProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#FF6B6B',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen
            name="Home"
            options={{ title: 'RoadPulse' }}
          >
            {(props) => <HomeScreen {...props} firebaseUid={DEVELOPMENT_FIREBASE_UID} />}
          </Stack.Screen>

          <Stack.Screen
            name="AddRoute"
            options={{ title: 'Add Route' }}
          >
            {(props) => <AddRouteScreen {...props} firebaseUid={DEVELOPMENT_FIREBASE_UID} />}
          </Stack.Screen>
        </Stack.Navigator>
      </NavigationContainer>
    </LocationProvider>
  );
}
