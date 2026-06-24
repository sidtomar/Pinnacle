import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function Doctor360Screen({ route }) {
  const { doctor: d } = route.params;
  const initials = d.name?.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  const scoreColor = d.engagement_score >= 80 ? '#059669' : d.engagement_score >= 50 ? '#D97706' : '#DC2626';

  function callWhatsApp() {
    if (d.whatsapp) Linking.openURL(`whatsapp://send?phone=${d.whatsapp.replace(/\D/g, '')}`);
  }

  return (
    <ScrollView style={s.container} contentContainerStyle={{ padding: 20 }}>
      {/* Header */}
      <View style={s.header}>
        <View style={s.avatar}>
          <Text style={s.initials}>{initials}</Text>
        </View>
        <View style={{ flex: 1 }}>
          <Text style={s.name}>{d.name}</Text>
          <Text style={s.meta}>{d.specialty} · {d.city}</Text>
          <Text style={s.hospital} numberOfLines={1}>{d.hospital}</Text>
        </View>
        <View style={[s.scoreBadge, { borderColor: scoreColor }]}>
          <Text style={[s.scoreNum, { color: scoreColor }]}>{d.engagement_score || d.pinnacle_score}</Text>
          <Text style={s.scoreLabel}>Score</Text>
        </View>
      </View>

      {/* KPIs */}
      <View style={s.kpiRow}>
        {[
          { label: 'Category', value: d.tier === 'A' ? 'A+' : 'A' },
          { label: 'SOW %', value: d.engagement_score ? `${d.engagement_score}%` : '—' },
          { label: 'Patients/Day', value: d.patients_per_day || '—' },
          { label: 'Experience', value: d.years_experience ? `${d.years_experience}y` : '—' },
        ].map(k => (
          <View key={k.label} style={s.kpi}>
            <Text style={s.kpiVal}>{k.value}</Text>
            <Text style={s.kpiLbl}>{k.label}</Text>
          </View>
        ))}
      </View>

      {/* Details */}
      <View style={s.section}>
        <Text style={s.sectionTitle}>Profile</Text>
        {[
          { label: 'Sub-specialty', value: d.sub_specialty },
          { label: 'Designation', value: d.designation },
          { label: 'State', value: d.state },
          { label: 'Email', value: d.email },
          { label: 'WhatsApp', value: d.whatsapp },
          { label: 'Clinical Interests', value: d.clinical_interests },
          { label: 'Last Contacted', value: d.last_contacted?.slice(0, 10) },
        ].filter(r => r.value).map(r => (
          <View key={r.label} style={s.row}>
            <Text style={s.rowLabel}>{r.label}</Text>
            <Text style={s.rowValue}>{r.value}</Text>
          </View>
        ))}
      </View>

      {/* Actions */}
      {d.whatsapp && (
        <TouchableOpacity style={s.waBtn} onPress={callWhatsApp}>
          <Ionicons name="logo-whatsapp" size={20} color="#fff" />
          <Text style={s.waBtnTxt}>Message on WhatsApp</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1, backgroundColor: '#F9FAFB' },
  header:       { flexDirection: 'row', gap: 14, alignItems: 'flex-start', marginBottom: 20 },
  avatar:       { width: 56, height: 56, borderRadius: 14, backgroundColor: '#EBF0F8', justifyContent: 'center', alignItems: 'center' },
  initials:     { fontSize: 18, fontWeight: '800', color: '#0B1628' },
  name:         { fontSize: 15, fontWeight: '800', color: '#0B1628' },
  meta:         { fontSize: 12, color: '#6B7280', marginTop: 2 },
  hospital:     { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  scoreBadge:   { borderWidth: 2, borderRadius: 10, padding: 8, alignItems: 'center', minWidth: 52 },
  scoreNum:     { fontSize: 18, fontWeight: '800' },
  scoreLabel:   { fontSize: 10, color: '#6B7280' },
  kpiRow:       { flexDirection: 'row', backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 1 },
  kpi:          { flex: 1, alignItems: 'center' },
  kpiVal:       { fontSize: 16, fontWeight: '800', color: '#0B1628' },
  kpiLbl:       { fontSize: 10, color: '#6B7280', marginTop: 2, textAlign: 'center' },
  section:      { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16 },
  sectionTitle: { fontSize: 13, fontWeight: '700', color: '#0B1628', marginBottom: 12 },
  row:          { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  rowLabel:     { fontSize: 12, color: '#6B7280', flex: 1 },
  rowValue:     { fontSize: 12, fontWeight: '600', color: '#0B1628', flex: 2, textAlign: 'right' },
  waBtn:        { backgroundColor: '#25D366', borderRadius: 12, padding: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  waBtnTxt:     { color: '#fff', fontWeight: '700', fontSize: 15 },
});
