import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import * as Sharing from 'expo-sharing';
import * as MailComposer from 'expo-mail-composer';
import { getContent } from '../services/api';

export default function ContentFeedScreen() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getContent()
      .then(r => setPapers((r.data.items || []).filter(p => p.status === 'approved')))
      .catch(() => setPapers([]))
      .finally(() => setLoading(false));
  }, []);

  async function shareWhatsApp(paper) {
    const msg = encodeURIComponent(`📄 ${paper.title}\n\n${paper.summary?.slice(0, 200)}...\n\n— PinnacleIQ`);
    const url = `whatsapp://send?text=${msg}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) Linking.openURL(url);
    else Alert.alert('WhatsApp not installed');
  }

  async function shareEmail(paper) {
    await MailComposer.composeAsync({
      subject: paper.title,
      body: `${paper.summary}\n\n— Shared via PinnacleIQ`,
    });
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color="#0B1628" />;

  return (
    <FlatList
      data={papers}
      keyExtractor={p => String(p.id)}
      contentContainerStyle={{ padding: 16 }}
      renderItem={({ item }) => (
        <View style={s.card}>
          <View style={s.tagRow}>
            <Text style={s.tag}>{item.specialty || item.cat}</Text>
            {item.therapy_area && item.therapy_area !== item.specialty &&
              <Text style={[s.tag, { backgroundColor: '#FEF3C7', color: '#92400E' }]}>{item.therapy_area}</Text>}
          </View>
          <Text style={s.title}>{item.title}</Text>
          <Text style={s.summary} numberOfLines={3}>{item.summary}</Text>
          <View style={s.actions}>
            <TouchableOpacity style={s.btn} onPress={() => shareWhatsApp(item)}>
              <Text style={s.btnTxt}>WhatsApp</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnEmail]} onPress={() => shareEmail(item)}>
              <Text style={[s.btnTxt, { color: '#0B1628' }]}>Email</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    />
  );
}

const s = StyleSheet.create({
  card:     { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  tagRow:   { flexDirection: 'row', gap: 6, marginBottom: 8 },
  tag:      { fontSize: 11, fontWeight: '600', backgroundColor: '#EFF6FF', color: '#1D4ED8', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  title:    { fontSize: 14, fontWeight: '700', color: '#0B1628', marginBottom: 6 },
  summary:  { fontSize: 12, color: '#6B7280', lineHeight: 18 },
  actions:  { flexDirection: 'row', gap: 8, marginTop: 12 },
  btn:      { flex: 1, backgroundColor: '#25D366', borderRadius: 8, padding: 10, alignItems: 'center' },
  btnEmail: { backgroundColor: '#F3F4F6' },
  btnTxt:   { color: '#fff', fontWeight: '700', fontSize: 13 },
});
