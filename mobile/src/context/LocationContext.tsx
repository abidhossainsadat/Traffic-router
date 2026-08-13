import React, { createContext, useContext, useState, useEffect } from 'react';
import * as Location from 'expo-location';

interface LocationContextType {
  currentLocation: Location.LocationObject | null;
  loading: boolean;
  error: string | null;
  requestPermission: () => Promise<void>;
  getCurrentPosition: () => Promise<void>;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export const LocationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentLocation, setCurrentLocation] = useState<Location.LocationObject | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const requestPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status !== 'granted') {
        setError('Location permission denied. Please enable location access in settings.');
        return;
      }

      await getCurrentPosition();
    } catch (err) {
      setError('Failed to request location permission');
      console.error(err);
    }
  };

  const getCurrentPosition = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
        timeout: 10000,
      });
      
      setCurrentLocation(location);
    } catch (err) {
      setError('Failed to get current location');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Request permission and get initial location on mount
    requestPermission();
  }, []);

  return (
    <LocationContext.Provider
      value={{
        currentLocation,
        loading,
        error,
        requestPermission,
        getCurrentPosition,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => {
  const context = useContext(LocationContext);
  if (context === undefined) {
    throw new Error('useLocation must be used within a LocationProvider');
  }
  return context;
};
