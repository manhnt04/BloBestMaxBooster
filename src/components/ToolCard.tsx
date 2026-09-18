import React from 'react';
import { StyleSheet, Switch, Text, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { GamingTool } from '../types';
import { COLORS } from '../theme/colors';

interface ToolCardProps {
  tool: GamingTool;
  onToggle: (id: string, value: boolean) => void;
}

export const ToolCard: React.FC<ToolCardProps> = ({ tool, onToggle }) => {
  return (
    <LinearGradient
      colors={['#121A2C', '#0B101C']}
      style={[styles.container, { borderColor: tool.enabled ? `${tool.color}66` : COLORS.borderDark }]}
    >
      <View style={styles.topRow}>
        <View style={[styles.iconWrapper, { backgroundColor: `${tool.color}22` }]}>
          <FontAwesome name={tool.icon as any} size={18} color={tool.color} />
        </View>

        <View style={styles.headerRight}>
          {tool.badge && (
            <View style={[styles.badge, { backgroundColor: `${tool.color}22`, borderColor: tool.color }]}>
              <Text style={[styles.badgeText, { color: tool.color }]}>{tool.badge}</Text>
            </View>
          )}
          <Switch
            value={tool.enabled}
            onValueChange={(val) => onToggle(tool.id, val)}
            thumbColor={tool.enabled ? tool.color : '#64748B'}
            trackColor={{ false: '#1E293B', true: `${tool.color}44` }}
          />
        </View>
      </View>

      <Text style={styles.title}>{tool.title}</Text>
      <Text style={styles.subtitle}>{tool.subtitle}</Text>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    margin: 5,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    minHeight: 125,
    justifyContent: 'space-between',
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconWrapper: {
    width: 38,
    height: 38,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
    borderWidth: 1,
  },
  badgeText: {
    fontSize: 9,
    fontWeight: '800',
  },
  title: {
    color: COLORS.textMain,
    fontSize: 12,
    fontWeight: '800',
    marginTop: 4,
  },
  subtitle: {
    color: COLORS.textSub,
    fontSize: 10,
    marginTop: 2,
    lineHeight: 14,
  },
});