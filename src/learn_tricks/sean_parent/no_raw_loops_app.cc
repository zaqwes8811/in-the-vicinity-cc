// http://channel9.msdn.com/Events/GoingNative/2013/Cpp-Seasoning
//

// Raw loop - A raw loop is any loop inside function where the function serve purpose larger then
// tha algorithm implemented by the loop.
//
//Why no raw loops?
//- Difficule reason about and dificult to prove post conditions
//- Error prone and likly to fail under non-obvios conditions
//- Introduce non-obvios performance problems
//- Complicates reasoning about the surronding code
// - отравляет код вокруг цикла
//
// Alternatives:
// - Use an existing alg. (Prefer standart algs if availabel)
// - Implement a know algorithm as a general function (contribute to library - внутреннюю или открытую
//   сперва нужно сделать как можно конкретнее, поюзать и понять где можно генереализовать)
// - Invent a new alg (Write a paper)
//
// No raw loops -> coding standart
//
// Use libs - Boost and ASL(похоже не развиватеся)
//
// ASL:
// http://stackoverflow.com/questions/6461621/how-to-compile-asl-boost-based-adobe-c-gui-library-on-linux
// http://stackoverflow.com/questions/2179999/c-adobe-source-libraries-impressions - 
// !! https://github.com/stlab/adobe_source_libraries
// Нужны какие-то потчи на буст. http://stlab.adobe.com/asl_readme.html
// http://stackoverflow.com/questions/6397501/how-to-compile-asl-boost-based-adobe-c-gui-library-on-windows-7
//
// Boost:
// Range: http://www.boost.org/doc/libs/1_41_0/libs/range/doc/boost_range.html
// http://stackoverflow.com/questions/13286876/boostrange-iterator-and-boostiterator-range-confusion - есть еще 
//   ссылка внутри, но там скорее к С++11
// Есть еще алгоритмы

#include <iostream>
#include <vector>
#include <algorithm>

// 3rdparty::common
#include <adobe/algorithm/find.hpp>
#include <adobe/algorithm/for_each.hpp>  // ничего не возвращает
#include <boost/range/iterator_range.hpp>
#include <boost/range/algorithm.hpp>
#include <boost/range/iterator.hpp>
#include <boost/bind.hpp>
//#include <boost/bind/placeholders.hpp>
/*
void PanelBar::RepositionExpandedPanels(Panel* fixed_panel) {
  int fixed_index = GetPanelIndex(expanded_panels_, *fixed_panel);

  const int center_x = fixed_panel->cur_panel_center();
  for (size_t i = 0; i < expanded_panels_.size(); ++i) {
    Panel* panel = expanded_panels_[i].get();

    //
    if (center_x <= panel->cur_panel_center() || i == expanded_panel_.size() - 1) {
      // если попалю сюда, то это в любом случае выход из цикла
      if (panel != fixed_panel) {
        ref_ptr<Panel> ref = expanded_panels_[fixed_index];
        expanded_panels_.erase(expanded_panels_.begin()+fixed_index);
        if (i < expanded_panels_.size()) {
            expanded_panels_.insert(expanded_panels_.begin() + i, ref);
        } else {
            expanded_panels_.push_back(ref);
        }
      }

      break;
    }
    //
  }
}*/

using std::rotate;
using std::stable_partition;
using std::pair;
using std::vector;
using std::ostream;
using std::for_each;
using std::back_insert_iterator;
using std::bind2nd;
using std::less;
using std::cout;
using std::endl;

namespace {
  
template <typename T>
class Action {
public:
  explicit Action(ostream* o_) : o(o_) { }
  void operator()(const T& elem) const {
    *o << elem << " ";
  }
  ostream* const o;
}; 
 
template <typename T>
ostream& operator<<(ostream& o, const vector<T>& a) 
{
  for_each(a.begin(), a.end(), Action<T>(&o));
  o << endl;
  return o;
}

//struct print
//{
    //template<typename T>
    void print(const int& t) //const
    {
        cout << t << " ";
    }
//};

struct Printer
{
    //template<typename T>
    void operator()(const int& t) const
    {
        cout << t << " ";
	//return 0;
    }
};

// Хорошо бы вернуть что-то - новое положение отрезка - [f_new, l_new)
// TODO: почему такое обобщение?
// TODO: похоже есть дыры
template <typename I >  // I models RandomAccessIterator
int /*pair<I, I>*/ slide(I f, I l, I p) {
  if (p < f) rotate(p, f, l);
  
  // Ветка выполняется!!
  if (l < p) {
    rotate(f, l, p);
    // [p, p+(l-f)) ?
  }
  
  // TODO: а остальные случаи
  
  return 0;
}

}

class IntSequence {
private:
  int value;
public:
  IntSequence(int init) : value(init) { }
  int operator()() {
    return value++;
  }
};

template <typename I, typename S>
pair<I, I> gather(I f, I l, I p, S s) {
  return make_pair(stable_partition(f, p, not1(s)), 
    stable_partition(p, l, s)
  );
}

// rotate
// stable_partition
// stable_sort
//
// For sorted:
// lower_bound 
int main() {
  // TODO: ошибочный ввод
  // first
  {
    int arr[] = {1, 2, 3, 8, 8, 8, 8, 7, 2, 1};
    const int kSize = sizeof(arr) / sizeof(arr[0]);
    vector<int> v;
    v.insert(v.begin(), arr, arr + kSize);
    vector<int>::iterator it = v.begin();
    cout << v;
    
    size_t f = 3;
    size_t l = 6+1;  // [)
    size_t p = kSize-1;  // )
    
    slide(it+f, it+l, it+p);
    
    cout << v;
    
    f = 5;
    l = kSize-1;  // [)
    p = 3;  // )
    
    slide(it+f, it+l, it+p);
    
    cout << v;
  }
  cout << endl;
  
  // second
  {
    int arr[] = {1, 2, 3, 8, 8, 8, 8, 7, 2, 1};
    const int kSize = sizeof(arr) / sizeof(arr[0]);
    vector<int> v;
    v.insert(v.begin(), arr, arr + kSize);
    vector<int>::iterator it = v.begin();
    cout << v;
    
    size_t edge = distance(v.begin(), v.end());
    pair<vector<int>::iterator, vector<int>::iterator> range 
      = gather(v.begin(), v.end(), v.begin()+edge, bind2nd(less<int>(), 4));
    
    cout << v;
    
    vector<int> tmp;
    copy(range.first, range.second, back_insert_iterator<std::vector<int> >(tmp));
    cout << tmp;
    
    // NO CHECK
    cout << *adobe::find(v, 8) << endl;
    
    //
    // Functors vs bind - http://stackoverflow.com/questions/17810018/functors-vs-stdbind
    /// Work
    //boost::for_each(boost::make_iterator_range(v.begin(), v.begin()+4) ,print());
    //
    /// Not work with functors
    // F - ConvertibleToFunction?
    // http://stackoverflow.com/questions/9453380/iterating-over-a-stdmap-using-boostbind
    // http://stlab.adobe.com/group__for__each.html
    // Указатель на функция передается, но объект нет.
    //adobe::for_each(make_pair(v.begin(), v.begin()+4), Printer());//&print); // With ptr work
    // boost::peaceholder::_1
    // http://stackoverflow.com/questions/356950/c-functors-and-their-uses
    //
    // Boost.Bind
    // http://www.boost.org/doc/libs/1_55_0/libs/bind/bind.html
    //adobe::for_each(v.begin(), v.begin()+4, &Printer::operator());
    cout << endl;
    
    /*
    IntSequence seq(1);
    // частичной специялизации похоже нет
    //generate_n<insert_iterator<vector<int> >, int, IntSequence&>(v.begin(), 4, seq); 
    generate_n<vector<int>::iterator, int, IntSequence&>(v.begin(), 4, seq);
    cout << v;
    
    generate_n<vector<int>::iterator, int, IntSequence&>(v.begin(), 4, seq);
    cout << v;
    */
  }
  
  
  return 0;
}
