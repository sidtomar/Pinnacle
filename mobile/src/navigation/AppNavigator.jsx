import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import TodayScreen from '../screens/TodayScreen';
import ContentFeedScreen from '../screens/ContentFeedScreen';
import ContentDetailScreen from '../screens/ContentDetailScreen';
import OccasionScreen from '../screens/OccasionScreen';
import DoctorDirectoryScreen from '../screens/DoctorDirectoryScreen';
import Doctor360Screen from '../screens/Doctor360Screen';

const Tab = createBottomTabNavigator();
const DoctorStack = createNativeStackNavigator();
const ContentStack = createNativeStackNavigator();

const NAVY = '#0B1628';
const GOLD = '#F59E0B';
const STACK_OPTS = { headerStyle: { backgroundColor: NAVY }, headerTintColor: '#fff', headerTitleStyle: { fontWeight: '700' } };

function DoctorStackNavigator() {
  return (
    <DoctorStack.Navigator screenOptions={STACK_OPTS}>
      <DoctorStack.Screen name="DoctorDirectory" component={DoctorDirectoryScreen} options={{ title: 'Doctor Directory' }} />
      <DoctorStack.Screen name="Doctor360"       component={Doctor360Screen}       options={({ route }) => ({ title: route.params?.doctor?.name || 'Doctor 360' })} />
    </DoctorStack.Navigator>
  );
}

function ContentStackNavigator() {
  return (
    <ContentStack.Navigator screenOptions={STACK_OPTS}>
      <ContentStack.Screen name="ContentFeed"   component={ContentFeedScreen}   options={{ title: 'Content Library' }} />
      <ContentStack.Screen name="ContentDetail" component={ContentDetailScreen} options={({ route }) => ({ title: (route.params?.paper?.title || 'Article').slice(0, 30) + '…' })} />
    </ContentStack.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: { backgroundColor: NAVY },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: '700' },
        tabBarActiveTintColor: GOLD,
        tabBarInactiveTintColor: '#6B7280',
        tabBarStyle: { backgroundColor: '#fff', borderTopColor: '#E5E7EB' },
        tabBarIcon: ({ color, size }) => {
          const icons = { Today: 'today-outline', Content: 'newspaper-outline', Doctors: 'people-outline', Occasions: 'calendar-outline' };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Today"     component={TodayScreen}            options={{ title: "Today's Tasks" }} />
      <Tab.Screen name="Content"   component={ContentStackNavigator}  options={{ headerShown: false, title: 'Content Library' }} />
      <Tab.Screen name="Doctors"   component={DoctorStackNavigator}   options={{ headerShown: false, title: 'Doctors' }} />
      <Tab.Screen name="Occasions" component={OccasionScreen}         options={{ title: 'Occasion Hub' }} />
    </Tab.Navigator>
  );
}
