import { StyleSheet, Text, View, TouchableOpacity, Alert, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { darkTheme } from '@/styles/theme';
import { apiPost } from '@/api/api';
import { useAuth } from '@/contexts/AuthContext';

type Category = 'age' | 'alcohol' | 'cleanliness' | 'gender' | 'noise' | 'hasPets' | 
                'politics' | 'sleepSchedule' | 'doesSmoke' | 'social';

const categories: Category[] = [
  'age',
  'alcohol',
  'cleanliness',
  'gender',
  'noise',
  'hasPets',
  'politics',
  'sleepSchedule',
  'doesSmoke',
  'social'
];

const dealbreakableCategories: Category[] = ['doesSmoke', 'hasPets', 'gender'];

const Preferences = () => {
  const [preferences, setPreferences] = useState<Record<Category, any>>({
    age: -1,
    alcohol: -1,
    cleanliness: -1,
    gender: '',
    noise: -1,
    hasPets: null,
    politics: -1,
    sleepSchedule: -1,
    doesSmoke: null,
    social: -1
  });
  const [dealbreakers, setDealbreakers] = useState<Category[]>([]);
  const { email, token } = useAuth();

  const handlePreferenceSelect = (category: Category, value: any) => {
    setPreferences(prev => ({ ...prev, [category]: value }));
  };

  const toggleDealbreaker = (category: Category) => {
    if (!dealbreakableCategories.includes(category)) {
      Alert.alert('Note', 'Only smoking, pets, and gender can be marked as dealbreakers.');
      return;
    }
    
    setDealbreakers(prev => prev.includes(category) ? prev.filter(item => item !== category) : [...prev, category]);
  };

  const handleSubmit = async () => {
    if (Object.values(preferences).includes(-1) || preferences.gender === '' || preferences.hasPets === null || preferences.doesSmoke === null) {
      Alert.alert('Error', 'Please set all preferences.');
      console.error('Invalid preference values detected:', preferences);
      return;
    }
  
    const preferencesWithDealbreakers = {
      ...preferences,
      smoking_dealbreaker: dealbreakers.includes('doesSmoke') ? 1 : 0,
      pets_dealbreaker: dealbreakers.includes('hasPets') ? 1 : 0,
      gender_dealbreaker: dealbreakers.includes('gender') ? 1 : 0
    };
  
    try {
      if (!token) {
        throw new Error("Invalid session token");
      }
      await apiPost('/set_preferences', { email, preferences: preferencesWithDealbreakers }, token);
      Alert.alert('Success', 'Preferences saved!');
    } catch (error: any) {
      Alert.alert('Error', error?.message || 'Something went wrong.');
    }
  };

  const capitalizeWord = (word: string): string => {
    return word.charAt(0).toUpperCase() + word.substring(1)
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Set Your Preferences</Text>
      <ScrollView style={styles.scrollContainer}>
        {categories.map(category => (
          <View key={category} style={styles.categoryContainer}>
            <Text style={styles.label}>{capitalizeWord(category)}</Text>
            {category === 'hasPets' || category === 'doesSmoke' ? (
              <View style={styles.optionsContainer}>
                {['Yes', 'No'].map(value => (
                  <TouchableOpacity
                    key={value}
                    style={[styles.option, preferences[category] === value && styles.selected]}
                    onPress={() => handlePreferenceSelect(category, value)}
                  >
                    <Text style={[styles.optionText, preferences[category] === value && styles.selectedText]}>
                      {value}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : category === 'gender' ? (
              <View style={styles.optionsContainer}>
                {['M', 'F'].map(value => (
                  <TouchableOpacity
                    key={value}
                    style={[styles.option, preferences.gender === value && styles.selected]}
                    onPress={() => handlePreferenceSelect('gender', value)}
                  >
                    <Text style={[styles.optionText, preferences.gender === value && styles.selectedText]}>
                      {value}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : (
              <View style={styles.optionsContainer}>
                {[1, 2, 3, 4, 5].map(value => (
                  <TouchableOpacity
                    key={value}
                    style={[styles.option, preferences[category] === value && styles.selected]}
                    onPress={() => handlePreferenceSelect(category, value)}
                  >
                    <Text style={[styles.optionText, preferences[category] === value && styles.selectedText]}>
                      {value}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
            {dealbreakableCategories.includes(category) && (
              <TouchableOpacity style={styles.dealbreakerButton} onPress={() => toggleDealbreaker(category)}>
                <Text style={[styles.dealbreakerText, dealbreakers.includes(category) && styles.dealbreakerActive]}>
                  {dealbreakers.includes(category) ? '✓ Dealbreaker' : 'Mark as Dealbreaker'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitButtonText}>Submit Preferences</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: darkTheme.background,
    paddingTop: 50,
  },
  scrollContainer: {
    flex: 1,
    padding: 20,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    color: darkTheme.text,
    padding: 20,
    paddingBottom: 10,
    backgroundColor: darkTheme.background,
  },
  categoryContainer: {
    marginBottom: 24,
    backgroundColor: darkTheme.background,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  label: {
    fontSize: 18,
    color: darkTheme.text,
    marginBottom: 12,
    fontWeight: '500',
  },
  optionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  option: {
    width: 50,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: darkTheme.border,
    borderRadius: 25,
  },
  selected: {
    backgroundColor: darkTheme.primary,
    borderColor: darkTheme.primary,
  },
  optionText: {
    color: darkTheme.text,
    fontSize: 16,
  },
  selectedText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  dealbreakerButton: {
    marginTop: 8,
    padding: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: darkTheme.primary,
    alignItems: 'center',
  },
  dealbreakerText: {
    color: darkTheme.primary,
    fontSize: 14,
    fontWeight: '500',
  },
  dealbreakerActive: {
    color: darkTheme.text,
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: darkTheme.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginVertical: 20,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default Preferences;