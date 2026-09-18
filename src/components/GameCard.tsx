import React from 'react';
import { Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { GameItem } from '../types';
import { COLORS } from '../theme/colors';

interface GameCardProps {
  game: GameItem;
  isPinned?: boolean;
  onLaunch: (game: GameItem) => void;
  onToggleBoost: (gameId: string) => void;
  onTogglePin?: (gameId: string) => void;
}

export const GameCard: React.FC<GameCardProps> = ({
  game,
  isPinned = false,
  onLaunch,
  onToggleBoost,
  onTogglePin,
}) => {
  const isImageIcon = game.icon && (game.icon.startsWith('data:image') || game.icon.startsWith('http'));

  return (
    <LinearGradient
      colors={['#131B2C', '#0A0E18']}
      style={[styles.card, { borderColor: isPinned ? COLORS.cyan : COLORS.borderDark }]}
    >
      <View style={styles.leftCol}>
        <View style={styles.iconContainer}>
          {isImageIcon ? (
            <Image source={{ uri: game.icon }} style={styles.appIcon} resizeMode="contain" />
          ) : (
            <View style={styles.fallbackIcon}>
              <Text style={styles.fallbackEmoji}>🎮</Text>
            </View>
          )}
        </View>

        <View style={styles.infoCol}>
          <View style={styles.nameRow}>
            <Text style={styles.name} numberOfLines={1}>{game.name}</Text>
            {isPinned && (
              <View style={styles.pinnedBadge}>
                <Text style={styles.pinnedBadgeText}>⭐ ĐÃ GHIM</Text>
              </View>
            )}
          </View>
          <Text style={styles.pkgName} numberOfLines={1}>
            {game.publisher ? `${game.publisher} • ` : ''}{game.packageName}
          </Text>
          <View style={styles.badgeRow}>
            <View style={styles.fpsBadge}>
              <Text style={styles.fpsBadgeText}>{game.targetFps} FPS</Text>
            </View>
            <Text style={styles.sizeText}>
              {game.sizeMB > 1000
                ? `${(game.sizeMB / 1024).toFixed(1)} GB`
                : `${Math.round(game.sizeMB)} MB`}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.actionsCol}>
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={() => onLaunch(game)}
          style={styles.launchBtn}
        >
          <LinearGradient
            colors={COLORS.reactorGrad}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.launchGrad}
          >
            <FontAwesome name="play" size={10} color="#000" style={{ marginRight: 4 }} />
            <Text style={styles.launchText}>CHƠI</Text>
          </LinearGradient>
        </TouchableOpacity>

        {onTogglePin && (
          <TouchableOpacity
            activeOpacity={0.7}
            onPress={() => onTogglePin(game.id)}
            style={styles.pinToggle}
          >
            <FontAwesome
              name={isPinned ? 'star' : 'star-o'}
              size={12}
              color={isPinned ? COLORS.amber : COLORS.textMuted}
            />
            <Text style={[styles.pinToggleText, isPinned && { color: COLORS.amber }]}>
              {isPinned ? 'Bỏ ghim' : 'Ghim'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  leftCol: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 10,
  },
  iconContainer: {
    width: 46,
    height: 46,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#1E293B',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  appIcon: {
    width: 46,
    height: 46,
    borderRadius: 12,
  },
  fallbackIcon: {
    width: 46,
    height: 46,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fallbackEmoji: {
    fontSize: 22,
  },
  infoCol: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  name: {
    color: COLORS.textMain,
    fontSize: 14,
    fontWeight: '800',
    flexShrink: 1,
  },
  pinnedBadge: {
    backgroundColor: 'rgba(255, 193, 7, 0.15)',
    paddingHorizontal: 5,
    paddingVertical: 1,
    borderRadius: 4,
    borderWidth: 0.5,
    borderColor: COLORS.amber,
  },
  pinnedBadgeText: {
    color: COLORS.amber,
    fontSize: 8,
    fontWeight: '800',
  },
  pkgName: {
    color: COLORS.textMuted,
    fontSize: 10,
    marginTop: 2,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 4,
  },
  fpsBadge: {
    backgroundColor: 'rgba(0, 242, 254, 0.15)',
    paddingHorizontal: 6,
    paddingVertical: 1,
    borderRadius: 4,
  },
  fpsBadgeText: {
    color: COLORS.cyan,
    fontSize: 9,
    fontWeight: '800',
  },
  sizeText: {
    color: COLORS.textMuted,
    fontSize: 10,
  },
  actionsCol: {
    alignItems: 'flex-end',
    gap: 6,
  },
  launchBtn: {
    borderRadius: 8,
    overflow: 'hidden',
  },
  launchGrad: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  launchText: {
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 0.5,
    color: '#000',
  },
  pinToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  pinToggleText: {
    fontSize: 10,
    color: COLORS.textMuted,
    fontWeight: '700',
  },
});