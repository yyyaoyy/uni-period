import java.util.*;


public class Lazyselect<T,U> implements Iterable<U> {

    private final Iterable<T> source;
    private final F<T,U> mapper;

    public Lazyselect(Iterable<T> source, F<T,U> mapper) {
        this.source = source;
        this.mapper = mapper;
    }

    public Iterator<U> iterator() {
        final Iterator<T> srcItr = source.iterator();
        return new Iterator<U>() {
            public boolean hasNext() {
                return srcItr.hasNext();
            }

            public void remove() {
                throw new UnsupportedOperationException();
            }

            public U next() {
                return mapper.apply(srcItr.next());
            }
        };
    }
    public static void main(String[] args) {
    }
}

