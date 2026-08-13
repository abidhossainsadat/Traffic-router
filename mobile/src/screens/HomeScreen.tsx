import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { routeService, Notification, Route as RouteType } from '../services/apiService';

type RootStackParamList = {
  Home: undefined;
  AddRoute: undefined;
  RouteDetail: { routeId: number };
};

type NavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

interface HomeScreenProps {
  firebaseUid: string;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ firebaseUid }) => {
  const navigation = useNavigation<NavigationProp>();
  const [routes, setRoutes] = useState<RouteType[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [routesData, notificationsData] = await Promise.all([
        routeService.getRoutes(firebaseUid),
        notificationService.getUnreadNotifications(firebaseUid),
      ]);
      setRoutes(routesData);
      setNotifications(notificationsData);
    } catch (err) {
      console.error('Failed to load data:', err);
      Alert.alert('Error', 'Failed to load routes. Please check your connection.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [firebaseUid]);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const getTrafficStatus = (route: RouteType) => {
    // This would fetch real-time traffic status from backend
    // For MVP, we'll show placeholder status
    return 'unknown'; // 'good', 'moderate', 'heavy', 'unknown'
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return '#4CAF50'; // Green
      case 'moderate':
        return '#FFC107'; // Yellow
      case 'heavy':
        return '#FF6B6B'; // Red
      default:
        return '#9E9E9E'; // Gray
    }
  };

  const renderRouteItem = ({ item }: { item: RouteType }) => {
    const status = getTrafficStatus(item);
    const statusColor = getStatusColor(status);

    return (
      <TouchableOpacity
        style={styles.routeCard}
        onPress={() => navigation.navigate('RouteDetail', { routeId: item.id })}
      >
        <View style={styles.routeHeader}>
          <Text style={styles.routeLabel}>{item.label}</Text>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusText}>{status.toUpperCase()}</Text>
          </View>
        </View>

        <Text style={styles.routeAddress} numberOfLines={1}>
          {item.origin_address || 'Origin'} → {item.destination_address || 'Destination'}
        </Text>

        <View style={styles.routeFooter}>
          <Text style={styles.threshold}>
            Alert at: {item.delay_threshold_minutes} min delay
          </Text>
          <Text style={styles.updatedAt}>
            Updated: {new Date(item.updated_at).toLocaleTimeString()}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  const renderNotificationItem = ({ item }: { item: Notification }) => (
    <View style={styles.notificationCard}>
      <Text style={styles.notificationMessage}>{item.message}</Text>
      <Text style={styles.notificationTime}>
        {new Date(item.sent_at).toLocaleString()}
      </Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Recent Notifications */}
      {notifications.length > 0 && (
        <View style={styles.notificationsSection}>
          <Text style={styles.sectionTitle}>Recent Alerts</Text>
          <FlatList
            data={notifications.slice(0, 3)}
            renderItem={renderNotificationItem}
            keyExtractor={(item) => item.id.toString()}
            horizontal
            showsHorizontalScrollIndicator={false}
          />
        </View>
      )}

      {/* Saved Routes */}
      <View style={styles.routesSection}>
        <View style={styles.routesHeader}>
          <Text style={styles.sectionTitle}>Your Routes</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => navigation.navigate('AddRoute')}
          >
            <Text style={styles.addButtonText}>+ Add Route</Text>
          </TouchableOpacity>
        </View>

        {routes.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No routes saved yet</Text>
            <Text style={styles.emptyStateSubtext}>
              Tap "Add Route" to start monitoring traffic
            </Text>
          </View>
        ) : (
          <FlatList
            data={routes}
            renderItem={renderRouteItem}
            keyExtractor={(item) => item.id.toString()}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
          />
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationsSection: {
    backgroundColor: '#fff',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  notificationCard: {
    backgroundColor: '#FFF3E0',
    padding: 12,
    borderRadius: 8,
    marginRight: 10,
    width: 280,
    borderLeftWidth: 4,
    borderLeftColor: '#FF6B6B',
  },
  notificationMessage: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5,
  },
  notificationTime: {
    fontSize: 12,
    color: '#666',
  },
  routesSection: {
    flex: 1,
    padding: 15,
  },
  routesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  addButton: {
    backgroundColor: '#FF6B6B',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  routeCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  routeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  routeLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  routeAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  routeFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 10,
  },
  threshold: {
    fontSize: 13,
    color: '#FF6B6B',
    fontWeight: '500',
  },
  updatedAt: {
    fontSize: 12,
    color: '#999',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});

export default HomeScreen;
