import { StyleSheet, Text, View, TouchableOpacity, Alert, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { darkTheme } from '@/styles/theme';
import { apiPost } from '@/api/api';
import { useAuth } from '@/contexts/AuthContext';

type Category = 'Age' | 'Alcohol' | 'Cleanliness' | 'Gender' | 'Noise' | 'Pets' | 
                'Politics' | 'Sleep Schedule' | 'Smoking' | 'Social';

const categories: Category[] = [
  'Age',
  'Alcohol',
  'Cleanliness',
  'Gender',
  'Noise',
  'Pets',
  'Politics',
  'Sleep Schedule',
  'Smoking',
  'Social'
];

const dealbreakableCategories: Category[] = ['Smoking', 'Pets', 'Gender'];

const Preferences = () => {
  const [preferences, setPreferences] = useState<Record<Category, number>>({
    'Age': -1,
    'Alcohol': -1,
    'Cleanliness': -1,
    'Gender': -1,
    'Noise': -1,
    'Pets': -1,
    'Politics': -1,
    'Sleep Schedule': -1,
    'Smoking': -1,
    'Social': -1
  });
  const [dealbreakers, setDealbreakers] = useState<Category[]>([]);
  const { email, token } = useAuth();

  const handlePreferenceSelect = (category: Category, value: number) => {
    setPreferences(prev => ({ ...prev, [category]: value }));
  };

  const toggleDealbreaker = (category: Category) => {
    if (!dealbreakableCategories.includes(category)) {
      Alert.alert('Note', 'Only Smoking, Pets, and Gender can be marked as dealbreakers.');
      return;
    }
    
    setDealbreakers((prev: Category[]) => {
      if (prev.includes(category)) {
        return prev.filter(item => item !== category);
      } else {
        return [...prev, category];
      }
    });
  };

  const handleSubmit = async () => {
    if (Object.values(preferences).includes(-1)) {
      Alert.alert('Error', 'Please set all preferences.');
      console.error('Invalid preference values detected:', preferences);
      return;
    }
  
    // Create a copy of preferences to add dealbreaker fields
    const preferencesWithDealbreakers = {
      ...preferences,
      smoking_dealbreaker: dealbreakers.includes('Smoking') ? 1 : 0,
      pets_dealbreaker: dealbreakers.includes('Pets') ? 1 : 0,
      gender_dealbreaker: dealbreakers.includes('Gender') ? 1 : 0
    };
  
    console.log(preferencesWithDealbreakers);
    console.log(email)
  
    try {
      if (!token) {
        throw new Error("Invalid session token");
      }
      await apiPost('/set_preferences', { 
        email,
        preferences: preferencesWithDealbreakers,
      }, token);
      Alert.alert('Success', 'Preferences saved!');
    } catch (error: any) {
      Alert.alert('Error', error?.message || 'Something went wrong.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Set Your Preferences</Text>
      <ScrollView style={styles.scrollContainer}>
        {categories.map(category => (
          <View key={category} style={styles.categoryContainer}>
            <Text style={styles.label}>{category}</Text>
            <View style={styles.optionsContainer}>
              {[1, 2, 3, 4, 5].map(value => (
                <TouchableOpacity
                  key={value}
                  style={[
                    styles.option,
                    preferences[category] === value && styles.selected
                  ]}
                  onPress={() => handlePreferenceSelect(category, value)}
                >
                  <Text style={[
                    styles.optionText,
                    preferences[category] === value && styles.selectedText
                  ]}>
                    {value}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            {dealbreakableCategories.includes(category) && (
              <TouchableOpacity 
                style={styles.dealbreakerButton}
                onPress={() => toggleDealbreaker(category)}
              >
                <Text style={[
                  styles.dealbreakerText,
                  dealbreakers.includes(category) && styles.dealbreakerActive
                ]}>
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