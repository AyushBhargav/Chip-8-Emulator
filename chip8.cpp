#include <iostream>
#include <vector>
#include <string>
#include "virtual_machine.h"

using namespace std;

int main() {
    vector<string> msg {"Hi", "there!"};

    for (const string& word: msg) {
        cout<<word<<" ";
    }
    cout<<endl;

    return 0;
}