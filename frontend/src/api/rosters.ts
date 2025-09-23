import apiClient, { apiRequest } from './apiClient';

export interface Roster {
  id: string;
  crewId: string;
  flightId: string | null;
  position: string;
  startTime: string;
  endTime: string;
  status: 'confirmed' | 'tentative' | 'cancelled' | 'on_sick_leave';
  dutyType: 'flight' | 'standby' | 'training' | 'rest';
  confidence: number;
  metadata: {
    briefingTime?: string;
    reportingTime?: string;
    estimatedBlockTime?: number;
    restPeriodBefore?: number;
    restPeriodAfter?: number;
    standbyLocation?: string;
    availableUntil?: string;
    replacementNeeded?: boolean;
  };
  violations: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    recommendation: string;
  }>;
  aiExplanation: string;
}

export interface RosterGeneration {
  id: string;
  assignments: Roster[];
  ai_confidence: number;
  metrics: {
    totalFlights: number;
    assignedFlights: number;
    unassignedFlights: number;
    totalViolations: number;
    avgConfidence: number;
    optimizationScore: number;
  };
  explanation_id?: string;
}

export interface DisruptionRequest {
  type: 'weather' | 'technical' | 'crew_unavailable' | 'security' | 'operational';
  affected: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  description?: string;
}

export interface DisruptionResponse {
  success: boolean;
  affected_assignments: string[];
  suggestion_id: string;
  recommendations: Array<{
    action: string;
    priority: number;
    description: string;
    estimatedImpact: string;
  }>;
}

export const rostersApi = {
  async getRosters(params: {
    start: string;
    end: string;
  }): Promise<{ rosters: Roster[] }> {
    return apiRequest(() =>
      apiClient.get<{ rosters: Roster[] }>('/rosters', { params })
    );
  },

  async generateRoster(params: {
    start: string;
    end: string;
  }): Promise<RosterGeneration> {
    return apiRequest(() =>
      apiClient.post<RosterGeneration>('/rosters/generate', params)
    );
  },

  async handleDisruption(
    disruption: DisruptionRequest
  ): Promise<DisruptionResponse> {
    return apiRequest(() =>
      apiClient.post<DisruptionResponse>('/rosters/disruptions', disruption)
    );
  },

  async optimizeRoster(rosterId: string): Promise<RosterGeneration> {
    return apiRequest(() =>
      apiClient.post<RosterGeneration>(`/rosters/${rosterId}/optimize`)
    );
  },

  async getExplanation(
    explanationId: string
  ): Promise<{ explanation: string; confidence: number }> {
    return apiRequest(() =>
      apiClient.get<{ explanation: string; confidence: number }>(
        `/explanations/${explanationId}`
      )
    );
  },
};
