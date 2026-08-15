import api from './api';

export interface Route {
  id: number;
  user_id: number;
  label: string;
  origin_lat: number;
  origin_lng: number;
  origin_address?: string;
  destination_lat: number;
  destination_lng: number;
  destination_address?: string;
  active_days: number[];
  active_time_start?: string;
  active_time_end?: string;
  delay_threshold_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TrafficCheck {
  id: number;
  route_id: number;
  checked_at: string;
  duration_normal?: number;
  duration_in_traffic?: number;
  delay_minutes?: number;
  incident_data?: any;
  ai_alert_message?: string;
  alert_sent: boolean;
}

export interface Notification {
  id: number;
  user_id: number;
  route_id: number;
  message: string;
  sent_at: string;
  delivery_status: string;
  error_message?: string;
}

export const routeService = {
  /**
   * Get all saved routes for the current user
   */
  async getRoutes(firebaseUid: string): Promise<Route[]> {
    const response = await api.get('/routes/', {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },

  /**
   * Create a new saved route
   */
  async createRoute(
    firebaseUid: string,
    routeData: {
      label: string;
      origin_lat: number;
      origin_lng: number;
      origin_address?: string;
      destination_lat: number;
      destination_lng: number;
      destination_address?: string;
      delay_threshold_minutes?: number;
      active_days?: number[];
      active_time_start?: string;
      active_time_end?: string;
    }
  ): Promise<Route> {
    const response = await api.post('/routes/', routeData, {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },

  /**
   * Update a route
   */
  async updateRoute(
    firebaseUid: string,
    routeId: number,
    updates: Partial<Route>
  ): Promise<Route> {
    const response = await api.patch(`/routes/${routeId}`, updates, {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },

  /**
   * Delete a route
   */
  async deleteRoute(firebaseUid: string, routeId: number): Promise<void> {
    await api.delete(`/routes/${routeId}`, {
      params: { firebase_uid: firebaseUid },
    });
  },

  /**
   * Get traffic history for a route
   */
  async getTrafficHistory(
    firebaseUid: string,
    routeId: number,
    limit: number = 100
  ): Promise<TrafficCheck[]> {
    const response = await api.get(`/routes/${routeId}/traffic-history`, {
      params: { firebase_uid: firebaseUid, limit },
    });
    return response.data;
  },
};

export const notificationService = {
  /**
   * Get recent notifications
   */
  async getNotifications(firebaseUid: string, limit: number = 50): Promise<Notification[]> {
    const response = await api.get('/notifications/', {
      params: { firebase_uid: firebaseUid, limit },
    });
    return response.data;
  },

  /**
   * Get unread notifications (last 24 hours)
   */
  async getUnreadNotifications(firebaseUid: string): Promise<Notification[]> {
    const response = await api.get('/notifications/unread', {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },
};

export const userService = {
  /**
   * Create a new user
   */
  async createUser(email: string, firebaseUid: string) {
    const response = await api.post('/users/', { email, firebase_uid: firebaseUid });
    return response.data;
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(firebaseUid: string) {
    const response = await api.get('/users/me', {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },

  /**
   * Get user's routes
   */
  async getUserRoutes(firebaseUid: string) {
    const response = await api.get('/users/me/routes', {
      params: { firebase_uid: firebaseUid },
    });
    return response.data;
  },
};
