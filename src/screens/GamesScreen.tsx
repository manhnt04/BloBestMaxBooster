import React, { useState } from 'react';
import { FlatList, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { GameCard } from '../components/GameCard';
import { GameItem } from '../types';
import { COLORS } from '../theme/colors';

interface GamesScreenProps {
  games: GameItem[];
  pinnedIds: string[];
  onLaunchGame: (game: GameItem) => void;
  onToggleBoostGame: (id: string) => void;
  onTogglePinGame: (id: string) => void;
}

export const GamesScreen: React.FC<GamesScreenProps> = ({
  games,
  pinnedIds,
  onLaunchGame,
  onToggleBoostGame,
  onTogglePinGame,
}) => {
  const [keyword, setKeyword] = useState('');
  const [filterMode, setFilterMode] = useState<'all' | 'pinned'>('all');

  const filtered = games
    .filter((g) => (filterMode === 'pinned' ? pinnedIds.includes(g.id) : true))
    .filter(
      (g) =>
        g.name.toLowerCase().includes(keyword.toLowerCase()) ||
        g.packageName.toLowerCase().includes(keyword.toLowerCase()) ||
        (g.publisher && g.publisher.toLowerCase().includes(keyword.toLowerCase()))
    );

  return (
    <View style={styles.container}>
      {/* Top Search Row */}
      <View style={styles.topRow}>
        <View style={styles.searchBox}>
          <FontAwesome name="search" size={13} color={COLORS.textMuted} style={{ marginRight: 8 }} />
          <TextInput
            style={styles.input}
            placeholder="Tìm theo tên game hoặc nhà phát hành..."
            placeholderTextColor={COLORS.textMuted}
            value={keyword}
            onChangeText={setKeyword}
          />
        </View>
      </View>

      {/* Filter Tabs */}
      <View style={styles.filterRow}>
        <TouchableOpacity
          onPress={() => setFilterMode('all')}
          style={[styles.filterChip, filterMode === 'all' && styles.filterChipActive]}
        >
          <Text style={[styles.filterChipText, filterMode === 'all' && styles.filterChipTextActive]}>
            🎮 Tất Cả Game ({games.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setFilterMode('pinned')}
          style={[styles.filterChip, filterMode === 'pinned' && styles.filterChipActive]}
        >
          <Text style={[styles.filterChipText, filterMode === 'pinned' && styles.filterChipTextActive]}>
            ⭐ Đã Ghim Trang Chủ ({pinnedIds.length})
          </Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionSubtitle}>
        Bấm nút "Ghim ⭐" để đưa tựa game bạn yêu thích hiển thị ngay ở màn hình Tăng Tốc!
      </Text>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <GameCard
            game={item}
            isPinned={pinnedIds.includes(item.id)}
            onLaunch={onLaunchGame}
            onToggleBoost={onToggleBoostGame}
            onTogglePin={onTogglePinGame}
          />
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <FontAwesome name="gamepad" size={40} color={COLORS.textMuted} />
            <Text style={styles.emptyTitle}>Không tìm thấy game phù hợp</Text>
            <Text style={styles.emptySubtitle}>
              Hãy thử tìm với từ khóa khác (ví dụ: Liên Quân, PUBG, VNG, Garena).
            </Text>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 30 }}
        showsVerticalScrollIndicator={false}
        removeClippedSubviews={true}
        maxToRenderPerBatch={6}
        initialNumToRender={8}
        windowSize={5}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
    paddingHorizontal: 14,
    paddingTop: 12,
  },
  topRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 10,
  },
  searchBox: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.bgCard,
    borderRadius: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: COLORS.borderDark,
    height: 42,
  },
  input: {
    flex: 1,
    color: COLORS.textMain,
    fontSize: 13,
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  filterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.borderDark,
  },
  filterChipActive: {
    borderColor: COLORS.cyan,
    backgroundColor: 'rgba(0, 242, 254, 0.12)',
  },
  filterChipText: {
    color: COLORS.textSub,
    fontSize: 11,
    fontWeight: '700',
  },
  filterChipTextActive: {
    color: COLORS.cyan,
    fontWeight: '800',
  },
  sectionSubtitle: {
    color: COLORS.textMuted,
    fontSize: 10,
    marginBottom: 10,
    fontStyle: 'italic',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 60,
    paddingHorizontal: 20,
  },
  emptyTitle: {
    color: COLORS.textMain,
    fontSize: 15,
    fontWeight: '800',
    marginTop: 12,
  },
  emptySubtitle: {
    color: COLORS.textMuted,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 6,
  },
});