import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useAuth } from '../context/AuthContext';

const TASKS = [
  { id: '1', type: 'Urgent',      doctor: 'Dr. Rajesh Kumar Sharma',  action: 'Send Birthday Wish',    spec: 'General Medicine', city: 'New Delhi' },
  { id: '2', type: 'Urgent',      doctor: 'Dr. Priya Reddy',          action: 'Send First Paper',      spec: 'Diabetology',      city: 'Chennai' },
  { id: '3', type: 'Urgent',      doctor: 'Dr. Sanjay Patel',         action: 'Re-engage',             spec: 'Diabetology',      city: 'Kolkata' },
  { id: '4', type: 'Recommended', doctor: 'Dr. Meena Chaudhary',      action: 'Share New Content',     spec: 'Gynaecology',      city: 'Chandigarh' },
  { id: '5', type: 'Recommended', doctor: 'Dr. Archana Rajan',        action: 'Follow Up',             spec: 'Gynaecology',      city: 'Mumbai' },
  { id: '6', type: 'Upcoming',    doctor: 'Dr. Padma Patel',          action: 'Diwali Greeting',       spec: 'Diabetology',      city: 'Lucknow' },
];

const TYPE_COLOR = { Urgent: '#EF4444', Recommended: '#F59E0B', Upcoming: '#6366F1' };

export default function TodayScreen() {
  const { user } = useAuth();

  return (
    <View style={s.container}>
      <View style={s.header}>
        <Text style={s.greeting}>Good morning, {user?.name?.split(' ')[0]} 👋</Text>
        <Text style={s.date}>{new Date().toDateString()}</Text>
      </View>
      <FlatList
        data={TASKS}
        keyExtractor={t => t.id}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => (
          <View style={s.card}>
            <View style={[s.badge, { backgroundColor: TYPE_COLOR[item.type] + '20' }]}>
              <Text style={[s.badgeTxt, { color: TYPE_COLOR[item.type] }]}>{item.type}</Text>
            </View>
            <Text style={s.doctor}>{item.doctor}</Text>
            <Text style={s.meta}>{item.spec} · {item.city}</Text>
            <View style={s.actionRow}>
              <Text style={s.actionTxt}>{item.action}</Text>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container:  { flex: 1, backgroundColor: '#F9FAFB' },
  header:     { backgroundColor: '#0B1628', padding: 20, paddingTop: 8 },
  greeting:   { color: '#fff', fontSize: 18, fontWeight: '700' },
  date:       { color: '#94A3B8', fontSize: 12, marginTop: 2 },
  card:       { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  badge:      { alignSelf: 'flex-start', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3, marginBottom: 8 },
  badgeTxt:   { fontSize: 11, fontWeight: '700' },
  doctor:     { fontSize: 14, fontWeight: '700', color: '#0B1628' },
  meta:       { fontSize: 12, color: '#6B7280', marginTop: 2 },
  actionRow:  { marginTop: 10, borderTopWidth: 1, borderTopColor: '#F3F4F6', paddingTop: 10 },
  actionTxt:  { fontSize: 13, color: '#F59E0B', fontWeight: '600' },
});

