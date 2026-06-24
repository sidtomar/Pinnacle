import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, Linking, Alert } from 'react-native';
import * as MailComposer from 'expo-mail-composer';
import { getContent } from '../services/api';

export default function ContentFeedScreen() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getContent()
      .then(r => {
        const items = r.data.items || r.data.content || r.data || [];
        setPapers(items.filter(p => p.status === 'approved'));
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function shareWhatsApp(paper) {
    const msg = encodeURIComponent(`📄 ${paper.title}\n\n${(paper.summary || paper.abstract || '').slice(0, 200)}...\n\n— PinnacleIQ`);
    const url = `whatsapp://send?text=${msg}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) Linking.openURL(url);
    else Alert.alert('WhatsApp not installed', 'Please install WhatsApp to use this feature.');
  }

  async function shareEmail(paper) {
    await MailComposer.composeAsync({
      subject: paper.title,
      body: `${paper.summary || paper.abstract || ''}\n\n— Shared via PinnacleIQ`,
    });
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color="#0B1628" />;
  if (error)   return <View style={s.center}><Text style={s.err}>⚠️ {error}</Text><Text style={s.errHint}>Is the backend running on port 8010?</Text></View>;
  if (!papers.length) return <View style={s.center}><Text style={s.empty}>No approved content yet.</Text><Text style={s.errHint}>Approve articles in the web app first.</Text></View>;

  return (
    <FlatList
      data={papers}
      keyExtractor={p => String(p.id)}
      contentContainerStyle={{ padding: 16 }}
      renderItem={({ item }) => (
        <View style={s.card}>
          <View style={s.tagRow}>
            <Text style={s.tag}>{item.specialty || item.cat}</Text>
            {item.therapy_area && item.therapy_area !== (item.specialty || item.cat) &&
              <Text style={[s.tag, { backgroundColor: '#FEF3C7', color: '#92400E' }]}>{item.therapy_area}</Text>}
          </View>
          <Text style={s.title}>{item.title}</Text>
          <Text style={s.summary} numberOfLines={3}>{item.summary || item.abstract || 'No summary available.'}</Text>
          <View style={s.actions}>
            <TouchableOpacity style={s.btnWA} onPress={() => shareWhatsApp(item)}>
              <Text style={s.btnWATxt}>📱 WhatsApp</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.btnEmail} onPress={() => shareEmail(item)}>
              <Text style={s.btnEmailTxt}>✉️ Email</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    />
  );
}

const s = StyleSheet.create({
  card:        { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  tagRow:      { flexDirection: 'row', gap: 6, marginBottom: 8, flexWrap: 'wrap' },
  tag:         { fontSize: 11, fontWeight: '600', backgroundColor: '#EFF6FF', color: '#1D4ED8', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  title:       { fontSize: 14, fontWeight: '700', color: '#0B1628', marginBottom: 6 },
  summary:     { fontSize: 12, color: '#6B7280', lineHeight: 18 },
  actions:     { flexDirection: 'row', gap: 8, marginTop: 12 },
  btnWA:       { flex: 1, backgroundColor: '#25D366', borderRadius: 8, padding: 10, alignItems: 'center' },
  btnWATxt:    { color: '#fff', fontWeight: '700', fontSize: 13 },
  btnEmail:    { flex: 1, backgroundColor: '#F3F4F6', borderRadius: 8, padding: 10, alignItems: 'center' },
  btnEmailTxt: { color: '#0B1628', fontWeight: '700', fontSize: 13 },
  center:      { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  err:         { fontSize: 14, color: '#EF4444', fontWeight: '600', textAlign: 'center' },
  errHint:     { fontSize: 12, color: '#6B7280', marginTop: 8, textAlign: 'center' },
  empty:       { fontSize: 14, color: '#374151', fontWeight: '600', textAlign: 'center' },
});
