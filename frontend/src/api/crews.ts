import apiClient, { apiRequest } from './apiClient';

export interface Crew {
  id: string;
  employeeNumber: string;
  firstName: string;
  lastName: string;
  position: 'Captain' | 'First Officer' | 'Flight Attendant';
  homeBase: string;
  qualifications: string[];
  licenseExpiry: string;
  medicalExpiry: string;
  totalHours: number;
  recentHours: number;
  status: 'available' | 'on_leave' | 'sick_leave' | 'training' | 'standby';
  preferences: {
    preferredRoutes: string[];
    avoidNightFlights: boolean;
    requestedDaysOff: string[];
  };
  dutyHistory: {
    currentWeekHours: number;
    currentMonthHours: number;
    lastRestPeriod: string;
    nextDutyStart: string;
  };
}

export interface Flight {
  id: string;
  flightNumber: string;
  aircraftType: string;
  route: {
    origin: string;
    destination: string;
    originName: string;
    destinationName: string;
  };
  schedule: {
    departureTime: string;
    arrivalTime: string;
    duration: number;
  };
  crew: {
    required: {
      captain: number;
      firstOfficer: number;
      flightAttendant: number;
    };
    assigned: {
      captain: string | null;
      firstOfficer: string | null;
      flightAttendant: string[];
    };
  };
  status: 'scheduled' | 'delayed' | 'cancelled' | 'unassigned' | 'partially_assigned';
  gate: string | null;
  aircraft: string;
  delayReason?: string;
  cancellationReason?: string;
  estimatedDeparture?: string;
}

export interface Disruption {
  id: string;
  type: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'resolved' | 'scheduled';
  affectedFlights: string[];
  affectedCrew: string[];
  startTime: string;
  estimatedEndTime: string;
  impactAssessment: {
    delayMinutes: number;
    crewDutyImpact: string;
    passengerImpact: string;
    operationalCost: string;
  };
  mitigationActions: string[];
  createdAt: string;
  updatedAt: string;
}

export const crewsApi = {
  async getCrews(): Promise<Crew[]> {
    return apiRequest(() => apiClient.get<Crew[]>('/crews'));
  },

  async getCrew(crewId: string): Promise<Crew> {
    return apiRequest(() => apiClient.get<Crew>(`/crews/${crewId}`));
  },

  async updateCrew(crewId: string, updates: Partial<Crew>): Promise<Crew> {
    return apiRequest(() =>
      apiClient.patch<Crew>(`/crews/${crewId}`, updates)
    );
  },

  async getFlights(): Promise<Flight[]> {
    return apiRequest(() => apiClient.get<Flight[]>('/flights'));
  },

  async getFlight(flightId: string): Promise<Flight> {
    return apiRequest(() => apiClient.get<Flight>(`/flights/${flightId}`));
  },

  async getDisruptions(): Promise<Disruption[]> {
    return apiRequest(() => apiClient.get<Disruption[]>('/disruptions'));
  },

  async createDisruption(
    disruption: Omit<Disruption, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<Disruption> {
    return apiRequest(() =>
      apiClient.post<Disruption>('/disruptions', disruption)
    );
  },

  async updateDisruption(
    disruptionId: string,
    updates: Partial<Disruption>
  ): Promise<Disruption> {
    return apiRequest(() =>
      apiClient.patch<Disruption>(`/disruptions/${disruptionId}`, updates)
    );
  }
};
