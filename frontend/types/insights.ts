export interface GenreInsight {
  genre: string;
  total_rated: number;
  watchlist_rated: number;
  average_rating: number;
  watchlist_average_rating: number;
  preference_score: number;
}

export interface ThemeInsight {
  tag: string;
  tag_id: number;
  movies_count: number;
  average_relevance: number;
  average_rating: number;
  preference_score: number;
}

export interface WatchlistMetrics {
  total_watchlist_items: number;
  items_rated: number;
  items_not_rated: number;
  completion_rate: number;
  average_rating: number | null;
  average_time_to_rate_hours: number | null;
  genres_in_watchlist: string[];
  most_common_watchlist_genre: string | null;
}

export interface UserInsights {
  user_id: string;
  generated_at: string;
  top_genre: string | null;
  top_3_genres: string[];
  genre_insights: GenreInsight[];
  top_theme: string | null;
  top_5_themes: string[];
  theme_insights: ThemeInsight[];
  watchlist_metrics: WatchlistMetrics;
  total_ratings: number;
  average_rating: number | null;
  rating_consistency: number | null;
}

export interface UserInsightsSummary {
  user_id: string;
  top_genre: string | null;
  top_3_genres: string[];
  top_theme: string | null;
  top_5_themes: string[];
  watchlist_completion_rate: number;
  total_ratings: number;
  generated_at: string;
}

export interface GlobalGenreStats {
  genre: string;
  total_ratings: number;
  average_rating: number;
  user_count: number;
  popularity_score: number;
}

export interface GlobalGenreLeaderboard {
  genres: GlobalGenreStats[];
  total_users: number;
  total_ratings: number;
}
