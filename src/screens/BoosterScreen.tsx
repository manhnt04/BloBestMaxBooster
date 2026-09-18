import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { StatCard } from '../components/StatCard';
import { ReactorCore } from '../components/ReactorCore';
import { ModeSelector } from '../components/ModeSelector';
import { GameCard } from '../components/GameCard';
import { GameItem, PerformanceMode, SystemStats } from '../types';
import { COLORS } from '../theme/colors';

interface BoosterScreenProps {
  stats: SystemStats;
  mode: PerformanceMode;
  pinnedGames: GameItem[];
  onBoostPress: () => void;
  onSelectMode: (mode: PerformanceMode) => void;
  onLaunchGame: (game: GameItem) => void;
  onToggleBoostGame: (id: string) => void;
  onNavigateToGames: () => void;
}

export const BoosterScreen: React.FC<BoosterScreenProps> = ({
  stats,
  mode,
  pinnedGames,
  onBoostPress,
  onSelectMode,
  onLaunchGame,
  onToggleBoostGame,
  onNavigateToGames,
}) => {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Real Hardware Gauges Row 1 */}
      <View style={styles.statsRow}>
        <StatCard
          title="Bộ Nhớ RAM Thật"
          value={`${stats.ramTotalGB} GB`}
          subValue={`${stats.ramUsedGB.toFixed(1)} GB Đang Dùng`}
          percentage={stats.ramUsedPercent}
          icon="microchip"
          color={stats.ramUsedPercent > 75 ? COLORS.orange : COLORS.cyan}
          accentGradient={stats.ramUsedPercent > 75 ? COLORS.beastGrad : COLORS.reactorGrad}
        />
        <StatCard
          title="Bộ Nhớ Trống"
          value={`${stats.freeStorageGB} GB`}
          subValue={`Tổng ${stats.totalStorageGB} GB`}
          percentage={Math.min(100, Math.round((stats.freeStorageGB / stats.totalStorageGB) * 100))}
          icon="hdd-o"
          color={COLORS.purple}
          accentGradient={COLORS.esportsGrad}
        />
      </View>

      {/* Real Hardware Gauges Row 2 */}
      <View style={styles.statsRow}>
        <StatCard
          title="Độ Trễ Ping Thật"
          value={`${stats.pingMs} ms`}
          subValue="Đến Cloudflare 1.1.1.1"
          percentage={Math.min(100, (stats.pingMs / 80) * 100)}
          icon="wifi"
          color={stats.pingMs < 30 ? COLORS.green : COLORS.amber}
          accentGradient={COLORS.ecoGrad}
        />
        <StatCard
          title="Pin & Nguồn Thật"
          value={`${stats.batteryPercent}%`}
          subValue={stats.isCharging ? 'Đang Sạc ⚡' : 'Đang Dùng Pin'}
          percentage={stats.batteryPercent}
          icon={stats.isCharging ? 'bolt' : 'battery-3'}
          color={stats.isCharging ? COLORS.amber : COLORS.green}
          accentGradient={COLORS.ecoGrad}
        />
      </View>

      {/* Central Cyber Reactor Core */}
      <ReactorCore
        isBoosted={stats.isHyperBoosted}
        onPressBoost={onBoostPress}
        fpsEstimate={stats.fpsEstimate}
      />

      {/* Performance Profile Selector */}
      <ModeSelector currentMode={mode} onSelectMode={onSelectMode} />

      {/* User Pinned Games Section */}
      <View style={styles.quickGamesSection}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>GAME ĐÃ GHIM CỦA BẠN</Text>
          <TouchableOpacity onPress={onNavigateToGames}>
            <Text style={styles.manageLink}>+ Thêm game</Text>
          </TouchableOpacity>
        </View>

        {pinnedGames.length > 0 ? (
          pinnedGames.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              isPinned={true}
              onLaunch={onLaunchGame}
              onToggleBoost={onToggleBoostGame}
            />
          ))
        ) : (
          <TouchableOpacity activeOpacity={0.8} onPress={onNavigateToGames} style={styles.emptyPinnedBox}>
            <FontAwesome name="star-o" size={24} color={COLORS.cyan} />
            <Text style={styles.emptyPinnedText}>Chưa ghim game nào ra trang chủ</Text>
            <Text style={styles.emptyPinnedSub}>Chạm vào đây để chọn ghim các tựa game bạn thường chơi nhất</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
  },
  content: {
    paddingBottom: 40,
    paddingTop: 10,
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 8,
  },
  quickGamesSection: {
    marginHorizontal: 12,
    marginTop: 14,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: 10,
  },
  sectionTitle: {
    color: COLORS.textSub,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.2,
    textTransform: 'uppercase',
  },
  manageLink: {
    color: COLORS.cyan,
    fontSize: 11,
    fontWeight: '700',
  },
  emptyPinnedBox: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 14,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: COLORS.borderDark,
  },
  emptyPinnedText: {
    color: COLORS.textMain,
    fontSize: 13,
    fontWeight: '800',
    marginTop: 8,
  },
  emptyPinnedSub: {
    color: COLORS.textMuted,
    fontSize: 11,
    textAlign: 'center',
    marginTop: 4,
  },
});