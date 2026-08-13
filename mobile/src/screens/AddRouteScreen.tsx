import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { routeService } from '../services/apiService';

type RootStackParamList = {
  Home: undefined;
  AddRoute: undefined;
};

type NavigationProp = StackNavigationProp<RootStackParamList, 'AddRoute'>;

interface AddRouteScreenProps {
  firebaseUid: string;
  initialOrigin?: { latitude: number; longitude: number; address?: string };
  initialDestination?: { latitude: number; longitude: number; address?: string };
}

export const AddRouteScreen: React.FC<AddRouteScreenProps> = ({
  firebaseUid,
  initialOrigin,
  initialDestination,
}) => {
  const navigation = useNavigation<NavigationProp>();
  const [label, setLabel] = useState('');
  const [originLat, setOriginLat] = useState(initialOrigin?.latitude.toString() || '');
  const [originLng, setOriginLng] = useState(initialOrigin?.longitude.toString() || '');
  const [originAddress, setOriginAddress] = useState(initialOrigin?.address || '');
  const [destinationLat, setDestinationLat] = useState(initialDestination?.latitude.toString() || '');
  const [destinationLng, setDestinationLng] = useState(initialDestination?.longitude.toString() || '');
  const [destinationAddress, setDestinationAddress] = useState(initialDestination?.address || '');
  const [threshold, setThreshold] = useState('10');
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    // Validation
    if (!label.trim()) {
      Alert.alert('Error', 'Please enter a route label (e.g., "Home to Work")');
      return;
    }

    const originLatNum = parseFloat(originLat);
    const originLngNum = parseFloat(originLng);
    const destLatNum = parseFloat(destinationLat);
    const destLngNum = parseFloat(destinationLng);

    if (isNaN(originLatNum) || isNaN(originLngNum) || isNaN(destLatNum) || isNaN(destLngNum)) {
      Alert.alert('Error', 'Please enter valid coordinates for origin and destination');
      return;
    }

    setLoading(true);

    try {
      await routeService.createRoute(firebaseUid, {
        label: label.trim(),
        origin_lat: originLatNum,
        origin_lng: originLngNum,
        origin_address: originAddress || undefined,
        destination_lat: destLatNum,
        destination_lng: destLngNum,
        destination_address: destinationAddress || undefined,
        delay_threshold_minutes: parseInt(threshold) || 10,
        active_days: [0, 1, 2, 3, 4], // Monday to Friday
        active_time_start: '07:30',
        active_time_end: '09:00',
      });

      Alert.alert('Success', 'Route saved successfully!', [
        {
          text: 'OK',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (err: any) {
      console.error('Failed to save route:', err);
      Alert.alert(
        'Error',
        err.response?.data?.detail || 'Failed to save route. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const useCurrentLocationAsOrigin = () => {
    // This would integrate with expo-location
    // For MVP, users can manually enter coordinates or select from map
    Alert.alert('Coming Soon', 'Use current location feature will be implemented soon.');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add New Route</Text>

      <TextInput
        style={styles.input}
        placeholder="Route Label (e.g., Home to Work)"
        value={label}
        onChangeText={setLabel}
        autoCapitalize="words"
      />

      <Text style={styles.sectionTitle}>Origin</Text>
      <TextInput
        style={styles.input}
        placeholder="Latitude"
        value={originLat}
        onChangeText={setOriginLat}
        keyboardType="decimal-pad"
      />
      <TextInput
        style={styles.input}
        placeholder="Longitude"
        value={originLng}
        onChangeText={setOriginLng}
        keyboardType="decimal-pad"
      />
      <TextInput
        style={styles.input}
        placeholder="Address (optional)"
        value={originAddress}
        onChangeText={setOriginAddress}
      />
      <TouchableOpacity style={styles.locationButton} onPress={useCurrentLocationAsOrigin}>
        <Text style={styles.locationButtonText}>📍 Use Current Location</Text>
      </TouchableOpacity>

      <Text style={styles.sectionTitle}>Destination</Text>
      <TextInput
        style={styles.input}
        placeholder="Latitude"
        value={destinationLat}
        onChangeText={setDestinationLat}
        keyboardType="decimal-pad"
      />
      <TextInput
        style={styles.input}
        placeholder="Longitude"
        value={destinationLng}
        onChangeText={setDestinationLng}
        keyboardType="decimal-pad"
      />
      <TextInput
        style={styles.input}
        placeholder="Address (optional)"
        value={destinationAddress}
        onChangeText={setDestinationAddress}
      />

      <Text style={styles.sectionTitle}>Alert Threshold</Text>
      <TextInput
        style={styles.input}
        placeholder="Delay in minutes (default: 10)"
        value={threshold}
        onChangeText={setThreshold}
        keyboardType="number-pad"
      />

      <TouchableOpacity
        style={[styles.saveButton, loading && styles.saveButtonDisabled]}
        onPress={handleSave}
        disabled={loading}
      >
        <Text style={styles.saveButtonText}>
          {loading ? 'Saving...' : 'Save Route'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 15,
    marginBottom: 8,
    color: '#555',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    fontSize: 16,
  },
  locationButton: {
    backgroundColor: '#f0f0f0',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  locationButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    backgroundColor: '#FF6B6B',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  saveButtonDisabled: {
    backgroundColor: '#ccc',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default AddRouteScreen;
