public class Median_of_medians {
    // Median of Medians Algorithm, Time complexity: O(n)
    public static int findKthSmallest(int[] A, int k) {
        int value = 0;
        int n = A.length;
        int c = 5; 		// Constant used to divide the array into columns

        while (true) {
            // Extract median of medians and take it as the pivot
            int pivot = findPivot(A, n, c);

            // Now count how many smaller and larger elements are there
            int smallerCount = 0;
            int largerCount = 0;

            int[] data = new int[2];

            // CountElements(a, n, pivot, out smallerCount, out largerCount);
            CountElements(A, n, pivot, data);

            smallerCount = data[0];
            largerCount = data[1];

            // Finally, partition the array
            if (k < smallerCount) {
                n = Partition(A, n, pivot, true);
            } else if (k < n - largerCount) {
                value = pivot;
                break;
            } else {
                k -= n - largerCount;
                n = Partition(A, n, pivot, false);
            }
        }
        return value;
    }

    private static int findPivot(int[] A, int n, int c) {
        while (n > 1) {
            int p = 0;
            int tmp = 0;

            for (int start = 0; start < n; start = start +c) {
                int end = start + c;
                if (end > n){ 	// Last column may have
                    end = n; 	// less than c elements
                }

                // Sort the column
                for (int i = start; i < end - 1; i++){
                    for (int j = i + 1; j < end; j++){
                        if (A[j] < A[i]) {
                            tmp = A[i];
                            A[i] = A[j];
                            A[j] = tmp;
                        }
                    }
                }

                // Pick the column's median and promote it
                // to the beginning of the array
                end = (start + end) / 2; // Median position
                tmp = A[end];
                A[end] = A[p];
                A[p++] = tmp;

            }
            n = p; // Reduce the array and repeat recursively
        }

        return A[0]; // Last median of medians is the pivot
    }

    // static void CountElements(int[] a, int n, int pivot, out int
    // smallerCount, out int largerCount)
    private static void CountElements(int[] a, int n, int pivot, int[] values) {
        for (int i = 0; i < n; i++) {
            if (a[i] < pivot)
                values[0]++;
            if (a[i] > pivot)
                values[1]++;
        }
    }

    private static int Partition(int[] a, int n, int pivot, boolean extractSmaller) {
        int p = 0;
        for (int i = 0; i < n; i++) {
            if ((extractSmaller && a[i] < pivot) || (!extractSmaller && a[i] > pivot)) {
                int tmp = a[i];
                a[i] = a[p];
                a[p++] = tmp;
            }
        }
        n = p;
        return n;
    }

    public static void main(String[] args) {
       // int[] a = { 4, 2, 1, 7, 5, 3, 8, 10, 9, 6 };
        int[] a = {62, 66, 70, 54, 74, 98, 83, 52, 80, 19};
        for (int k = 0; k < a.length; k++) {
            int value = findKthSmallest(a, k);
            System.out.println(k + "th smallest num is " + value);
        }
    }

}
