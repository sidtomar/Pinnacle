import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Linking, Alert } from 'react-native';
import * as MailComposer from 'expo-mail-composer';

export default function ContentDetailScreen({ route, navigation }) {
  const { paper: p } = route.params;

  async function shareWhatsApp() {
    const msg = encodeURIComponent(`📄 ${p.title}\n\n${(p.summary || p.abstract || '').slice(0, 500)}\n\n— PinnacleIQ`);
    const url = `whatsapp://send?text=${msg}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) Linking.openURL(url);
    else Alert.alert('WhatsApp not installed');
  }

  async function shareEmail() {
    await MailComposer.composeAsync({
      subject: p.title,
      body: `${p.summary || p.abstract || ''}\n\n${p.article || ''}\n\n— Shared via PinnacleIQ`,
      isHtml: false,
    });
  }

  const spec = p.specialty || p.cat || '—';
  const therapy = p.therapy_area || p.therapy || '';
  const journal = p.journal || p.source || '';
  const author = p.author || p.authors || '';

  return (
    <View style={s.container}>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }}>
        {/* Tags */}
        <View style={s.tagRow}>
          <Text style={s.tagBlue}>{spec}</Text>
          {therapy && therapy.toLowerCase() !== spec.toLowerCase() &&
            <Text style={s.tagAmber}>{therapy}</Text>}
          {p.status && <Text style={s.tagGreen}>{p.status}</Text>}
        </View>

        {/* Title */}
        <Text style={s.title}>{p.title}</Text>

        {/* Meta */}
        {journal ? <Text style={s.meta}>📰 {journal}</Text> : null}
        {author  ? <Text style={s.meta}>✍️ {author}</Text> : null}
        {p.pub_date || p.date ? <Text style={s.meta}>📅 {p.pub_date || p.date}</Text> : null}

        {/* Summary */}
        <View style={s.section}>
          <Text style={s.sectionTitle}>Summary</Text>
          <Text style={s.body}>{p.summary || p.abstract || 'No summary available.'}</Text>
        </View>

        {/* Full Article */}
        {(p.article || p.full_text) ? (
          <View style={s.section}>
            <Text style={s.sectionTitle}>Full Article</Text>
            <Text style={s.body}>{p.article || p.full_text}</Text>
          </View>
        ) : null}

        {/* Key Findings / Tags */}
        {p.tags && p.tags.length > 0 && (
          <View style={s.section}>
            <Text style={s.sectionTitle}>Tags</Text>
            <View style={s.chipRow}>
              {p.tags.filter(t => t !== 'AI Pipeline').map((t, i) => (
                <Text key={i} style={s.chip}>{t}</Text>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Sticky share bar */}
      <View style={s.shareBar}>
        <TouchableOpacity style={s.btnWA} onPress={shareWhatsApp}>
          <Text style={s.btnWATxt}>📱 Share via WhatsApp</Text>
        </TouchableOpacity>
        <TouchableOpacity style={s.btnEmail} onPress={shareEmail}>
          <Text style={s.btnEmailTxt}>✉️ Email</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1, backgroundColor: '#F9FAFB' },
  tagRow:       { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 12 },
  tagBlue:      { fontSize: 11, fontWeight: '600', backgroundColor: '#EFF6FF', color: '#1D4ED8', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  tagAmber:     { fontSize: 11, fontWeight: '600', backgroundColor: '#FEF3C7', color: '#92400E', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  tagGreen:     { fontSize: 11, fontWeight: '600', backgroundColor: '#D1FAE5', color: '#065F46', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  title:        { fontSize: 18, fontWeight: '800', color: '#0B1628', lineHeight: 24, marginBottom: 12 },
  meta:         { fontSize: 12, color: '#6B7280', marginBottom: 4 },
  section:      { marginTop: 20 },
  sectionTitle: { fontSize: 14, fontWeight: '700', color: '#0B1628', marginBottom: 8, borderBottomWidth: 1, borderBottomColor: '#E5E7EB', paddingBottom: 6 },
  body:         { fontSize: 13, color: '#374151', lineHeight: 20 },
  chipRow:      { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  chip:         { fontSize: 11, backgroundColor: '#F3F4F6', color: '#374151', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  shareBar:     { position: 'absolute', bottom: 0, left: 0, right: 0, flexDirection: 'row', gap: 8, padding: 16, backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#E5E7EB' },
  btnWA:        { flex: 2, backgroundColor: '#25D366', borderRadius: 10, padding: 14, alignItems: 'center' },
  btnWATxt:     { color: '#fff', fontWeight: '700', fontSize: 14 },
  btnEmail:     { flex: 1, backgroundColor: '#F3F4F6', borderRadius: 10, padding: 14, alignItems: 'center' },
  btnEmailTxt:  { color: '#0B1628', fontWeight: '700', fontSize: 14 },
});
