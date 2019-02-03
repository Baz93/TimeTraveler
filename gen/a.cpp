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
		m = sz(a[0]);
		return 1;
	}

	void init (const Input &input) {
		*this = input;
	}
};

struct Data: Input {
	int ans_t, ans_m;

	void write () {
		cout << ans_t << ' ' << ans_m << endl;
	}
};


namespace Main {
	
	struct Solution: Data {
		struct state {
			ve<ve<bool>> box,
			ve<pa<pii, pii>> players;
		}

		state initial_state() {
			state res;
			res.box = ve<ve<bool>>(n, ve<bool>(m))
			pii start = mp(-1, -1);
			pii finish = mp(-1, -1);
			for (int i = 0; i < n; ++i) {
				for (int j = 0; j < m; ++j) {
					res.box[i][j] = (a[i][j] == 'X');
					if (a[i][j] == '.') {
						start = mp(i, j);
					}
					if (a[i][j] == '@') {
						finish = mp(i, j);
					}
				}
			}
			res.players.pb(mp(mp(startx, starty), mp(finishx, finishy)));
		}

		bool is_finish(const state &s) {
			return sz(s.players) == 0;
		}

		ve<state> get_moves(const state &s) {
			result = ve<state>();
			

			return result;
		}

		int bfs (int cnt) {
			ve<pa<state, int>> q;
			q.pb(mp(initial_state(), 0));
			for (const auto &p : q) {
				for (const auto &s : get_moves(p.fs)) {
					if (is_finish(s)) {
						return p.sc + 1;
					}
					q.pb(mp(s, p.sc + 1));
				}
			}
			return -1;
		}

		void solve () {
			for (int i = 0; i <= 4; ++i) {
				int d = bfs(i);
				if (d != -1) {
					ans_t = i;
					ans_m = d;
					return;
				}
			}
			ans_t = 5;
			ans_m = -1;
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
