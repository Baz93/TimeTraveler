#include <bits/stdc++.h>
using namespace std;

#ifdef SG
	#include <debug.h>
#else
	template<typename T> struct outputer;
	struct outputable {};
	#define PRINT(...)
	#define OUTPUT(...)
	#define show(...)
	#define debug(...)
	#define deepen(...)
	#define timer(...)
	#define fbegin(...)
	#define fend
	#define pbegin(...)
	#define pend
#endif

#define ARG4(_1,_2,_3,_4,...) _4

#define forn3(i,l,r) for (int i = int(l); i < int(r); ++i)
#define forn2(i,n) forn3 (i, 0, n)
#define forn(...) ARG4(__VA_ARGS__, forn3, forn2) (__VA_ARGS__)

#define ford3(i,l,r) for (int i = int(r) - 1; i >= int(l); --i)
#define ford2(i,n) ford3 (i, 0, n)
#define ford(...) ARG4(__VA_ARGS__, ford3, ford2) (__VA_ARGS__)

#define ve vector
#define pa pair
#define tu tuple
#define mp make_pair
#define mt make_tuple
#define pb emplace_back
#define fs first
#define sc second
#define all(a) (a).begin(), (a).end()
#define sz(a) ((int)(a).size())

typedef long double ld;
typedef int64_t ll;
typedef uint64_t ull;
typedef uint32_t ui;
typedef uint16_t us;
typedef uint8_t uc;
typedef pa<int, int> pii;
typedef pa<int, ll> pil;
typedef pa<ll, int> pli;
typedef pa<ll, ll> pll;
typedef ve<int> vi;

template<typename T> inline auto sqr (T x) -> decltype(x * x) {return x * x;}
template<typename T1, typename T2> inline bool umx (T1& a, T2 b) {if (a < b) {a = b; return 1;} return 0;}
template<typename T1, typename T2> inline bool umn (T1& a, T2 b) {if (b < a) {a = b; return 1;} return 0;}

struct Input {
	int n, m;
	ve<string> a;

	bool read () {
		string s;
		while (getline(cin, s) && sz(s)) {
			a.pb(s);
		}
		n = sz(a);
		if (n == 0) {
			return 0;
		}
		m = sz(a[0]);
		return 1;
	}

	void write_input () {
		for (const auto &s : a) {
			cout << s << endl;
		}
	}

	void gen (int n_, int m_) {
		n = n_;
		m = m_;
		a = ve<string>(n, string(m, ' '));
		forn (i, n) {
			forn (j, m) {
				a[i][j] = " X#"[rand() % 3];
			}
		}
		a[rand() % n][rand() % m] = '.';
		while (1) {
			int x = rand() % n;
			int y = rand() % m;
			if (a[x][y] != '.') {
				a[x][y] = '@';
				break;
			}
		}
	}

	void init (const Input &input) {
		*this = input;
	}
};

struct Data: Input {
	int ans;

	void write () {
		cout << ans << endl;
	}
};


namespace Main {
	const int dx[4] = {1, 0, -1, 0};
	const int dy[4] = {0, 1, 0, -1};
	
	struct Solution: Data {
		struct state {
			ve<ve<bool>> box;
			ve<pa<pii, pii>> players;

			void normalize () {
				sort(all(players));
			}

			typedef pa<ve<ve<bool>>, ve<pa<pii, pii>>> key_type;

			key_type key () const {
				return mp(box, players);
			}
		};

		bool out_of_grid (int x, int y) {
			return x < 0 || x >= n || y < 0 || y >= m;
		}

		bool is_player_passable (const state &s, int x, int y) {
			if (out_of_grid(x, y)) {
				return 0;
			}
			if (a[x][y] == '#') {
				return 0;
			}
			if (s.box[x][y]) {
				return 0;
			}
			for (const auto &p : s.players) {
				if (p.fs == mp(x, y)) {
					return 0;
				}
			}
			return 1;
		}

		bool is_box_passable (const state &s, int x, int y) {
			if (!is_player_passable(s, x, y)) {
				return 0;
			}
			if (a[x][y] == '@') {
				return 0;
			}
			return 1;
		}

		state initial_state() {
			state res;
			res.box = ve<ve<bool>>(n, ve<bool>(m));
			pii start = mp(-1, -1);
			pii finish = mp(-1, -1);
			forn (i, n) {
				forn (j, m) {
					res.box[i][j] = (a[i][j] == 'X');
					if (a[i][j] == '.') {
						start = mp(i, j);
					}
					if (a[i][j] == '@') {
						finish = mp(i, j);
					}
				}
			}
			res.players.pb(mp(start, finish));
			return res;
		}

		bool is_finish(const state &s) {
			return sz(s.players) == 0;
		}

		ve<state> get_moves(const state &s) {
			ve<state> result;
			if (sz(s.players) < 4) {
				forn (i, n) {
					forn (j, m) {
						if (!is_player_passable(s, i, j)) {
							continue;
						}
						auto t = s;
						t.players.pb(mp(mp(i, j), mp(i, j)));
						t.normalize();
						result.pb(t);
					}
				}
			}
			forn (i, sz(s.players)) {
				forn (j, sz(s.players)) {
					if (i == j && sz(s.players) > 1) {
						continue;
					}
					if (s.players[i].fs != s.players[j].sc) {
						continue;
					}
					auto t = s;
					t.players[j].sc = t.players[i].sc;
					swap(t.players[i], t.players.back());
					t.players.pop_back();
					t.normalize();
					result.pb(t);
				}
			}
			forn (i, sz(s.players)) {
				int x0 = s.players[i].fs.fs;
				int y0 = s.players[i].fs.sc;
				forn (d, 4) {
					int x1 = x0 + dx[d];
					int y1 = y0 + dy[d];
					int x2 = x1 + dx[d];
					int y2 = y1 + dy[d];
					if (out_of_grid(x1, y1)) {
						continue;
					}
					if (is_player_passable(s, x1, y1)) {
						auto t = s;
						t.players[i].fs = mp(x1, y1);
						t.normalize();
						result.pb(t);
					} else if (s.box[x1][y1] && is_box_passable(s, x2, y2)) {
						auto t = s;
						t.players[i].fs = mp(x1, y1);
						t.box[x1][y1] = 0;
						t.box[x2][y2] = 1;
						t.normalize();
						result.pb(t);
					}
				}
			}
			return result;
		}

		int bfs () {
			set<state::key_type> mem;
			ve<pa<state, int>> q;
			auto add = [&] (const state &s, int d) {
				q.pb(mp(s, d));
				mem.insert(s.key());
			};
			add(initial_state(), 0);
			forn (i, sz(q)) {
				for (const auto &s : get_moves(q[i].fs)) {
					if (mem.count(s.key())) {
						continue;
					}
					if (is_finish(s)) {
						return q[i].sc + 1;
					}
					add(s, q[i].sc + 1);
				}
			}
			return -1;
		}

		void solve () {
			ans = bfs();
		}
		
		void clear () {
			*this = Solution();
		}
	};
}


Main::Solution sol;

int main () {
	cout.setf(ios::showpoint | ios::fixed);
	cout.precision(20);

//	int mx = -1;
//	Input best;
//	int n = 4, m = 5;
//
//	srand(time(nullptr));
//	while (clock() < 60 * CLOCKS_PER_SEC) {
//		Input in;
//		in.gen(n, m);
//		sol.init(in);
//		sol.solve();
//		int res = sol.ans;
//		sol.clear();
//
//		if (umx(mx, res)) {
//			best = in;
//		}
//	}
//	cout << mx << endl;
//	best.write_input();
//
//	return 0;

	#ifdef SG
		freopen((problemname + ".in").c_str(), "r", stdin);
//		freopen((problemname + ".out").c_str(), "w", stdout);
		while (sol.read()) {
			sol.solve();
			sol.write();
			sol.clear();
		}
	#else
		sol.read();
		sol.solve();
		sol.write();
	#endif
	
	/*
	int t;
	cin >> t;
	forn (i, t) {
		sol.read();
		sol.solve();
		sol.write();
		sol.clear();
	}
	*/
	
	return 0;
}
