// BFS and DFS algorithms for unweighted graph
// Checked results at https://graphonline.ru/en/

#include <stdbool.h>
#include <stdio.h>

#define TOTAL_VERTICES 8

bool adjacency_matrix[TOTAL_VERTICES][TOTAL_VERTICES] = {					// I've been lazy and made this global
	{ 0,1,0,0,0,0,1,0 },													// 0 = no edge / 1 = edge
	{ 1,0,0,0,1,0,0,0 },													// with int instead of bool, this could hold weighted graph data
	{ 0,1,0,0,0,0,1,0 },
	{ 1,0,0,0,1,0,0,0 },
	{ 0,1,0,1,0,1,0,0 },
	{ 0,0,0,0,1,0,0,0 },
	{ 0,1,0,0,0,1,0,0 },
	{ 0,0,0,0,0,0,1,0 }
};


void perform_BFS(int start_vertex);											// breadth-first search
void perform_DFS(int vertex, bool visited[]);								// depth-first-search
int  pick_start_vertex();													// determine search entry
void show_graph();															// print adjacency matrix



// Successively perform BFS and DFS

int main() {
	printf("Breadth-First Search and Depth-First Search Demo\n\n");
	show_graph();

	printf("BFS TRAVERSAL -- ");
	perform_BFS(pick_start_vertex());										// I like this line :)

	printf("DFS TRAVERSAL -- ");
	bool visited[TOTAL_VERTICES] = { false };
	perform_DFS(pick_start_vertex(), visited);								// visited[] will always be passed for the recursion

	return 0;
}


// Breadth-First Search algorithm (non-recursive)
// Perform BFS starting at given start_vertex
// Put first vertex in queue
// Dequeue current vertex, then check vertex table and enqueue all adjacent unvisited vertices
// Do this until the queue stays empty

void perform_BFS(int start_vertex) {
	int  queue[TOTAL_VERTICES];												// set up a queue as an int array to hold vertices to be processed
	int  front = -1, rear = -1;
	bool visited[TOTAL_VERTICES] = { false };								// info table for vertex status (visited / non visited)

	printf("Visiting vertex %d (%c).\n", start_vertex + 1, 'A' + start_vertex);			// initialize traversal,
	visited[start_vertex] = true;											// mark start_vertex as visited
	queue[++rear] = start_vertex;											// and enqueue start_vertex

	while(front < rear) {													// continue BFS while queue not empty
		int current_vertex = queue[++front];								// dequeue vertex number and update queue status
		for(int i = 0; i < TOTAL_VERTICES; i++) {							// traverse vertex table and enqueue unvisited adjacent vertives
			if(adjacency_matrix[current_vertex][i] && !visited[i]) {		// or "==1"; but this code would work with weighted graphs as well
				printf("Visiting vertex %d (%c).\n", i + 1, 'A' + i);		// print info
				visited[i] = true;											// mark current_vertex as visited
				queue[++rear] = i;											// enqueue adjacent vertex and update queue status
			}
		}
	}
	printf("\n");
}


// Depth-First Search algorithm (recursive)
// Perform recursive BFS starting at given vertex
// Mark current vertex as visited, traverse vertex list to find first unvisited adjacent vertex and start recursion for this vertex

void perform_DFS(int vertex, bool visited[]) {
	visited[vertex] = true;													// mark vertex as visited
	printf("Visiting vertex %d (%c).\n", vertex + 1, 'A' + vertex);			// print info

	for(int i = 0; i < TOTAL_VERTICES; i++) {								// traverse complete vertex table
		if(adjacency_matrix[vertex][i] && !visited[i]) {					// or "==1"; but this code would work with weighted graphs as well
			perform_DFS(i, visited);										// if connection and not visited: recursion
		}
	}
}


// Pick a starting point from the existing vertices
// User choice is return value

int pick_start_vertex() {
	int pick;

	printf("Please choose start vertex from 1 (A) to %d (%c)", TOTAL_VERTICES, 'A' + TOTAL_VERTICES - 1);
	do {																	// repeat until number is within expected range
		printf(": ");
		scanf("%d", &pick);
	} while(pick < 1 || pick > TOTAL_VERTICES);

	return --pick;
}


// Print adjacency_matrix

void show_graph() {
	printf("   A B C D E F G H\n");
	for(int i = 0; i < TOTAL_VERTICES; i++) {
		printf("%c  ", 'A' + i);
		for (int j = 0; j < TOTAL_VERTICES; j++) {
			printf("%d ", adjacency_matrix[i][j]);
		}
		printf("\n");
	}
	printf("\nC (3) and H (8) are only accessible as start vertices and cannot be both accessed in one run.\n\n");
}